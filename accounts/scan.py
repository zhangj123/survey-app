import io

import qrcode
from django.contrib.auth import login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from qrcode.image.svg import SvgPathImage

from .forms import LoginForm
from .models import ScanLoginTicket


def _ticket_url(request, ticket):
    return request.build_absolute_uri(reverse("accounts:qr_confirm", args=[ticket.id]))


@require_POST
def qr_create(request, provider):
    if provider not in ScanLoginTicket.Provider.values:
        return JsonResponse({"error": "不支持的登录方式"}, status=400)
    ticket = ScanLoginTicket.objects.create(provider=provider)
    return JsonResponse(
        {
            "id": str(ticket.id),
            "status_url": reverse("accounts:qr_status", args=[ticket.id]),
            "claim_url": reverse("accounts:qr_claim", args=[ticket.id]),
            "qr_url": reverse("accounts:qr_image", args=[ticket.id]),
            "confirm_url": reverse("accounts:qr_confirm", args=[ticket.id]),
        }
    )


@require_GET
def qr_image(request, pk):
    ticket = get_object_or_404(ScanLoginTicket, pk=pk)
    img = qrcode.make(_ticket_url(request, ticket), image_factory=SvgPathImage, box_size=10, border=1)
    buf = io.BytesIO()
    img.save(buf)
    return HttpResponse(buf.getvalue(), content_type="image/svg+xml")


@require_GET
def qr_status(request, pk):
    ticket = get_object_or_404(ScanLoginTicket, pk=pk)
    status = ticket.status
    if ticket.expired() and status == ScanLoginTicket.Status.PENDING:
        status = "expired"
    return JsonResponse({"status": status})


@require_POST
def qr_claim(request, pk):
    ticket = get_object_or_404(ScanLoginTicket, pk=pk)
    if ticket.expired() or ticket.status != ScanLoginTicket.Status.CONFIRMED or not ticket.user:
        return JsonResponse({"error": "二维码已失效，请刷新"}, status=400)
    login(request, ticket.user)
    ticket.status = ScanLoginTicket.Status.CLAIMED
    ticket.save(update_fields=["status"])
    return JsonResponse({"ok": True, "redirect": reverse("surveys:list")})


def qr_confirm(request, pk):
    ticket = get_object_or_404(ScanLoginTicket, pk=pk)
    if ticket.expired() or ticket.status == ScanLoginTicket.Status.CLAIMED:
        return render(request, "accounts/scan_expired.html", {"ticket": ticket})

    if request.method == "POST":
        if not request.user.is_authenticated:
            form = LoginForm(request, data=request.POST)
            if form.is_valid():
                login(request, form.get_user())
            else:
                return render(
                    request,
                    "accounts/scan_confirm.html",
                    {"ticket": ticket, "form": form},
                )
        ticket.user = request.user
        ticket.status = ScanLoginTicket.Status.CONFIRMED
        ticket.confirmed_at = timezone.now()
        ticket.save()
        return render(request, "accounts/scan_done.html", {"ticket": ticket})

    form = None if request.user.is_authenticated else LoginForm(request)
    return render(request, "accounts/scan_confirm.html", {"ticket": ticket, "form": form})
