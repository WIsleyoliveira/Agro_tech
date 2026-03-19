# market_routes.py - Rotas do mercado local (produtor / comprador / transportador)
import os, shutil
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

from auth import get_current_user
from market_database import market_db

router = APIRouter(prefix="/api/market", tags=["Mercado Local"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────────
# MODELOS PYDANTIC
# ──────────────────────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    user_type: str
    cnpj: Optional[str] = None
    company_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    bio: Optional[str] = None
    whatsapp: Optional[str] = None

class DealStatusUpdate(BaseModel):
    status: str
    transport_fee: Optional[float] = None
    transporter_id: Optional[int] = None

class MessageSend(BaseModel):
    receiver_id: int
    content: str
    deal_id: Optional[int] = None

class DealCreate(BaseModel):
    listing_id: int

class RatingCreate(BaseModel):
    deal_id: int
    rated_id: int
    stars: int
    comment: Optional[str] = None

# ──────────────────────────────────────────────────────────────
# PERFIS
# ──────────────────────────────────────────────────────────────

@router.put("/profile")
async def update_profile(data: ProfileUpdate,
                          current_user: dict = Depends(get_current_user)):
    valid_types = {"produtor", "comprador", "transportador"}
    if data.user_type not in valid_types:
        raise HTTPException(400, "Tipo inválido.")
    if data.cnpj:
        cnpj_digits = ''.join(filter(str.isdigit, data.cnpj))
        if len(cnpj_digits) != 14:
            raise HTTPException(400, "CNPJ inválido.")
    result = market_db.upsert_profile(
        user_id=current_user["user_id"], user_type=data.user_type,
        cnpj=data.cnpj, company_name=data.company_name,
        city=data.city, state=data.state, bio=data.bio, whatsapp=data.whatsapp
    )
    if not result.get("success"):
        raise HTTPException(500, result.get("error", "Erro ao salvar perfil"))
    return {"success": True, "message": "Perfil atualizado com sucesso"}


@router.get("/profile/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    profile = market_db.get_profile(current_user["user_id"])
    if not profile:
        raise HTTPException(404, "Perfil não encontrado")
    ratings = market_db.get_user_ratings(current_user["user_id"])
    return {**profile, "rating_avg": ratings["average"], "rating_count": ratings["count"]}


@router.get("/profile/{user_id}")
async def get_user_profile(user_id: int,
                            current_user: dict = Depends(get_current_user)):
    profile = market_db.get_profile(user_id)
    if not profile:
        raise HTTPException(404, "Usuário não encontrado")
    ratings = market_db.get_user_ratings(user_id)
    listings = market_db.get_my_listings(user_id)
    active = [l for l in listings if l["status"] == "disponivel"]
    return {**profile, "rating_avg": ratings["average"], "rating_count": ratings["count"],
            "ratings": ratings["ratings"][:5], "active_listings": active}


# ──────────────────────────────────────────────────────────────
# CNPJ
# ──────────────────────────────────────────────────────────────

def validate_cnpj_digits(cnpj: str) -> bool:
    digits = ''.join(filter(str.isdigit, cnpj))
    if len(digits) != 14 or len(set(digits)) == 1:
        return False
    def calc(ds, w):
        t = sum(int(d)*x for d,x in zip(ds,w))
        r = t % 11
        return 0 if r < 2 else 11-r
    w1=[5,4,3,2,9,8,7,6,5,4,3,2]; w2=[6,5,4,3,2,9,8,7,6,5,4,3,2]
    return digits[12]==str(calc(digits[:12],w1)) and digits[13]==str(calc(digits[:13],w2))

@router.get("/cnpj/validate/{cnpj}")
async def validate_cnpj(cnpj: str):
    valid = validate_cnpj_digits(cnpj)
    return {"cnpj": cnpj, "valid": valid,
            "message": "CNPJ válido" if valid else "CNPJ inválido"}


# ──────────────────────────────────────────────────────────────
# PUBLICAÇÕES (LISTINGS)
# ──────────────────────────────────────────────────────────────

@router.post("/listings")
async def create_listing(
    title: str = Form(...), description: str = Form(""),
    crop: str = Form(...), quantity_kg: float = Form(...),
    price_per_kg: float = Form(...), city: str = Form(...), state: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    image_path = None
    if image and image.filename:
        ext = image.filename.rsplit(".", 1)[-1].lower()
        if ext not in {"jpg","jpeg","png","webp"}:
            raise HTTPException(400, "Imagem deve ser JPG, PNG ou WEBP")
        filename = f"{uuid4().hex}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        image_path = f"/static/uploads/{filename}"

    result = market_db.create_listing(
        user_id=current_user["user_id"], title=title, description=description,
        crop=crop, quantity_kg=quantity_kg, price_per_kg=price_per_kg,
        city=city, state=state, image_path=image_path
    )
    if not result.get("success"):
        raise HTTPException(500, result.get("error", "Erro ao criar publicação"))
    return {"success": True, "listing_id": result["listing_id"],
            "message": "Publicação criada com sucesso!"}


@router.get("/listings")
async def list_listings(
    state: Optional[str] = None, crop: Optional[str] = None,
    min_price: Optional[float] = None, max_price: Optional[float] = None,
    min_qty: Optional[float] = None, order_by: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Lista publicações com preço médio da cultura para comparação"""
    listings = market_db.get_listings_with_price_avg(state=state, crop=crop)

    # Filtros extras
    if min_price is not None:
        listings = [l for l in listings if (l["price_per_kg"] or 0) >= min_price]
    if max_price is not None:
        listings = [l for l in listings if (l["price_per_kg"] or 0) <= max_price]
    if min_qty is not None:
        listings = [l for l in listings if (l["quantity_kg"] or 0) >= min_qty]

    # Ordenação
    if order_by == "price_asc":
        listings.sort(key=lambda x: x.get("price_per_kg") or 0)
    elif order_by == "price_desc":
        listings.sort(key=lambda x: x.get("price_per_kg") or 0, reverse=True)
    elif order_by == "qty_desc":
        listings.sort(key=lambda x: x.get("quantity_kg") or 0, reverse=True)

    # Adiciona indicador de preço
    for l in listings:
        avg = l.get("crop_avg_price")
        if avg and avg > 0 and l.get("price_per_kg"):
            diff = ((l["price_per_kg"] - avg) / avg) * 100
            l["price_vs_avg_pct"] = round(diff, 1)
            if diff <= -10:
                l["price_badge"] = "🔥 Abaixo da média"
            elif diff >= 10:
                l["price_badge"] = "⬆️ Acima da média"
            else:
                l["price_badge"] = None
        else:
            l["price_vs_avg_pct"] = None
            l["price_badge"] = None

    return {"success": True, "total": len(listings), "listings": listings}


@router.get("/listings/mine")
async def my_listings(current_user: dict = Depends(get_current_user)):
    listings = market_db.get_my_listings(current_user["user_id"])
    return {"success": True, "listings": listings}


@router.get("/listings/{listing_id}")
async def get_listing(listing_id: int,
                       current_user: dict = Depends(get_current_user)):
    listing = market_db.get_listing(listing_id)
    if not listing:
        raise HTTPException(404, "Publicação não encontrada")
    ratings = market_db.get_user_ratings(listing["user_id"])
    return {**listing, "producer_rating": ratings["average"],
            "producer_rating_count": ratings["count"]}


@router.delete("/listings/{listing_id}")
async def delete_listing(listing_id: int,
                          current_user: dict = Depends(get_current_user)):
    deleted = market_db.delete_listing(listing_id, current_user["user_id"])
    if not deleted:
        raise HTTPException(403, "Você não pode remover esta publicação")
    return {"success": True, "message": "Publicação removida"}


# ──────────────────────────────────────────────────────────────
# NEGOCIAÇÕES (DEALS)
# ──────────────────────────────────────────────────────────────

@router.post("/deals")
async def start_deal(data: DealCreate, current_user: dict = Depends(get_current_user)):
    listing = market_db.get_listing(data.listing_id)
    if not listing:
        raise HTTPException(404, "Publicação não encontrada")
    if listing["status"] != "disponivel":
        raise HTTPException(400, "Esta publicação não está mais disponível")
    if listing["user_id"] == current_user["user_id"]:
        raise HTTPException(400, "Você não pode comprar sua própria publicação")
    result = market_db.create_deal(
        listing_id=data.listing_id, buyer_id=current_user["user_id"],
        producer_id=listing["user_id"]
    )
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Erro ao iniciar negociação"))
    # Notifica o produtor
    market_db.create_notification(
        user_id=listing["user_id"], ntype="new_deal",
        title="💼 Nova proposta de negócio!",
        body=f"{current_user.get('name','Comprador')} quer negociar: {listing['title']}",
        deal_id=result["deal_id"]
    )
    return {"success": True, "deal_id": result["deal_id"],
            "message": "Negociação iniciada! Envie uma mensagem para o produtor."}


@router.get("/deals")
async def my_deals(current_user: dict = Depends(get_current_user)):
    deals = market_db.get_my_deals(current_user["user_id"])
    return {"success": True, "deals": deals}


@router.get("/deals/transports")
async def open_transports(current_user: dict = Depends(get_current_user)):
    transports = market_db.get_open_transports()
    return {"success": True, "transports": transports}


@router.get("/deals/{deal_id}")
async def get_deal(deal_id: int, current_user: dict = Depends(get_current_user)):
    deal = market_db.get_deal(deal_id)
    if not deal:
        raise HTTPException(404, "Negócio não encontrado")
    uid = current_user["user_id"]
    if uid not in (deal["buyer_id"], deal["producer_id"], deal.get("transporter_id")):
        raise HTTPException(403, "Sem permissão para ver este negócio")
    # Indica se o usuário já avaliou
    deal["can_rate"] = (deal["status"] in ("concluido","entregue")
                        and market_db.can_rate(deal_id, uid))
    return deal


@router.patch("/deals/{deal_id}/status")
async def update_deal(deal_id: int, data: DealStatusUpdate,
                       current_user: dict = Depends(get_current_user)):
    deal = market_db.get_deal(deal_id)
    if not deal:
        raise HTTPException(404, "Negócio não encontrado")
    uid = current_user["user_id"]
    valid_statuses = {"fechado","recusado","cancelado","em_transporte","concluido","negociando","entregue"}
    if data.status not in valid_statuses:
        raise HTTPException(400, f"Status inválido.")

    result = market_db.update_deal_status(
        deal_id, data.status,
        transport_fee=data.transport_fee,
        transporter_id=data.transporter_id or (uid if data.status == "em_transporte" else None)
    )

    if data.status == "fechado":
        market_db.update_listing_status(deal["listing_id"], "vendido")
        # Notifica o comprador
        market_db.create_notification(
            user_id=deal["buyer_id"], ntype="deal_accepted",
            title="✅ Negócio aceito!",
            body=f"Seu negócio para '{deal['listing_title']}' foi aceito pelo produtor.",
            deal_id=deal_id
        )
    elif data.status == "em_transporte":
        market_db.create_notification(
            user_id=deal["producer_id"], ntype="transport_assigned",
            title="🚛 Transportador confirmado!",
            body=f"Um transportador assumiu o frete de '{deal['listing_title']}'.",
            deal_id=deal_id
        )
        market_db.create_notification(
            user_id=deal["buyer_id"], ntype="transport_assigned",
            title="🚛 Produto em transporte!",
            body=f"'{deal['listing_title']}' está a caminho.",
            deal_id=deal_id
        )
    elif data.status == "entregue":
        market_db.create_notification(
            user_id=deal["buyer_id"], ntype="delivered",
            title="📦 Produto entregue!",
            body=f"'{deal['listing_title']}' foi marcado como entregue. Avalie o produtor!",
            deal_id=deal_id
        )
        market_db.create_notification(
            user_id=deal["producer_id"], ntype="delivered",
            title="📦 Entrega confirmada!",
            body=f"'{deal['listing_title']}' foi entregue. Avalie o comprador!",
            deal_id=deal_id
        )
    elif data.status == "recusado":
        market_db.create_notification(
            user_id=deal["buyer_id"], ntype="deal_refused",
            title="❌ Negócio recusado",
            body=f"O produtor recusou o negócio para '{deal['listing_title']}'.",
            deal_id=deal_id
        )

    if not result.get("success"):
        raise HTTPException(500, "Erro ao atualizar status")
    status_labels = {
        "fechado": "Negócio fechado!", "recusado": "Negócio recusado.",
        "cancelado": "Negócio cancelado.", "em_transporte": "Você assumiu o transporte!",
        "concluido": "Negócio concluído!", "negociando": "Voltou para negociação.",
        "entregue": "Entrega confirmada! Agora você pode avaliar."
    }
    return {"success": True, "message": status_labels.get(data.status, "Status atualizado")}


# ──────────────────────────────────────────────────────────────
# MENSAGENS (CHAT INTERNO)
# ──────────────────────────────────────────────────────────────

@router.post("/messages")
async def send_message(data: MessageSend, current_user: dict = Depends(get_current_user)):
    result = market_db.send_message(
        sender_id=current_user["user_id"], receiver_id=data.receiver_id,
        content=data.content, deal_id=data.deal_id
    )
    if not result.get("success"):
        raise HTTPException(500, "Erro ao enviar mensagem")
    # Notifica o destinatário
    market_db.create_notification(
        user_id=data.receiver_id, ntype="new_message",
        title=f"💬 Nova mensagem de {current_user.get('name','alguém')}",
        body=data.content[:80] + ("..." if len(data.content) > 80 else ""),
        deal_id=data.deal_id
    )
    return {"success": True, "message_id": result["message_id"]}


@router.get("/messages/inbox")
async def get_inbox(current_user: dict = Depends(get_current_user)):
    inbox = market_db.get_inbox(current_user["user_id"])
    unread = market_db.count_unread(current_user["user_id"])
    return {"success": True, "inbox": inbox, "unread_total": unread}


@router.get("/messages/deal/{deal_id}")
async def get_deal_messages(deal_id: int, current_user: dict = Depends(get_current_user)):
    deal = market_db.get_deal(deal_id)
    if not deal:
        raise HTTPException(404, "Negócio não encontrado")
    uid = current_user["user_id"]
    if uid not in (deal["buyer_id"], deal["producer_id"], deal.get("transporter_id")):
        raise HTTPException(403, "Sem permissão")
    # Marca mensagens E notificações deste deal como lidas
    market_db.mark_messages_read(uid, deal_id)
    msgs = market_db.get_conversation(0, 0, deal_id=deal_id)
    return {"success": True, "messages": msgs, "deal": deal}


@router.get("/messages/unread")
async def unread_count(current_user: dict = Depends(get_current_user)):
    count = market_db.count_unread(current_user["user_id"])
    return {"unread": count}


# ──────────────────────────────────────────────────────────────
# AVALIAÇÕES (RATINGS)
# ──────────────────────────────────────────────────────────────

@router.post("/ratings")
async def create_rating(data: RatingCreate, current_user: dict = Depends(get_current_user)):
    if not 1 <= data.stars <= 5:
        raise HTTPException(400, "Avaliação deve ser entre 1 e 5 estrelas.")
    deal = market_db.get_deal(data.deal_id)
    if not deal:
        raise HTTPException(404, "Negócio não encontrado.")
    if deal["status"] not in ("concluido", "entregue"):
        raise HTTPException(400, "Só é possível avaliar negócios concluídos ou entregues.")
    uid = current_user["user_id"]
    if uid not in (deal["buyer_id"], deal["producer_id"]):
        raise HTTPException(403, "Sem permissão para avaliar este negócio.")
    if not market_db.can_rate(data.deal_id, uid):
        raise HTTPException(400, "Você já avaliou este negócio.")
    result = market_db.create_rating(
        deal_id=data.deal_id, rater_id=uid,
        rated_id=data.rated_id, stars=data.stars, comment=data.comment
    )
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Erro ao salvar avaliação."))
    market_db.create_notification(
        user_id=data.rated_id, ntype="new_rating",
        title=f"⭐ Você recebeu {data.stars} estrela(s)!",
        body=data.comment or "Sem comentário.",
        deal_id=data.deal_id
    )
    return {"success": True, "message": "Avaliação enviada!"}


@router.get("/ratings/{user_id}")
async def get_ratings(user_id: int, current_user: dict = Depends(get_current_user)):
    ratings = market_db.get_user_ratings(user_id)
    return {"success": True, **ratings}


# ──────────────────────────────────────────────────────────────
# NOTIFICAÇÕES
# ──────────────────────────────────────────────────────────────

@router.get("/notifications")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    notifs = market_db.get_notifications(current_user["user_id"])
    unread = market_db.count_unread_notifications(current_user["user_id"])
    return {"success": True, "notifications": notifs, "unread": unread}


@router.patch("/notifications/read")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    market_db.mark_notifications_read(current_user["user_id"])
    return {"success": True}


@router.patch("/notifications/{notif_id}/read")
async def mark_one_read(notif_id: int, current_user: dict = Depends(get_current_user)):
    market_db.mark_notifications_read(current_user["user_id"], notif_id)
    return {"success": True}


# ──────────────────────────────────────────────────────────────
# DASHBOARD / STATS
# ──────────────────────────────────────────────────────────────

@router.get("/stats/me")
async def my_stats(current_user: dict = Depends(get_current_user)):
    stats = market_db.get_producer_stats(current_user["user_id"])
    return {"success": True, **stats}


# ──────────────────────────────────────────────────────────────
# PERFIS
# ──────────────────────────────────────────────────────────────

@router.put("/profile")
async def update_profile(data: ProfileUpdate,
                          current_user: dict = Depends(get_current_user)):
    """Cria ou atualiza o perfil de tipo (produtor/comprador/transportador)"""
    valid_types = {"produtor", "comprador", "transportador"}
    if data.user_type not in valid_types:
        raise HTTPException(400, "Tipo inválido. Use: produtor, comprador ou transportador")

    # Se for comprador, CNPJ é opcional mas validamos o formato se informado
    if data.cnpj:
        cnpj_digits = ''.join(filter(str.isdigit, data.cnpj))
        if len(cnpj_digits) != 14:
            raise HTTPException(400, "CNPJ inválido. Deve ter 14 dígitos.")

    result = market_db.upsert_profile(
        user_id=current_user["user_id"],
        user_type=data.user_type,
        cnpj=data.cnpj,
        company_name=data.company_name,
        city=data.city,
        state=data.state,
        bio=data.bio,
        whatsapp=data.whatsapp
    )
    if not result.get("success"):
        raise HTTPException(500, result.get("error", "Erro ao salvar perfil"))
    return {"success": True, "message": "Perfil atualizado com sucesso"}


@router.get("/profile/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    profile = market_db.get_profile(current_user["user_id"])
    if not profile:
        raise HTTPException(404, "Perfil não encontrado")
    return profile


@router.get("/profile/{user_id}")
async def get_user_profile(user_id: int,
                            current_user: dict = Depends(get_current_user)):
    profile = market_db.get_profile(user_id)
    if not profile:
        raise HTTPException(404, "Usuário não encontrado")
    return profile


# ──────────────────────────────────────────────────────────────
# VALIDAÇÃO DE CNPJ (offline — dígitos verificadores)
# ──────────────────────────────────────────────────────────────

def validate_cnpj_digits(cnpj: str) -> bool:
    """Valida CNPJ pelos dígitos verificadores, sem precisar de internet"""
    digits = ''.join(filter(str.isdigit, cnpj))
    if len(digits) != 14 or len(set(digits)) == 1:
        return False

    def calc(digits_str, weights):
        total = sum(int(d) * w for d, w in zip(digits_str, weights))
        rest = total % 11
        return 0 if rest < 2 else 11 - rest

    w1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    w2 = [6,5,4,3,2,9,8,7,6,5,4,3,2]
    d1 = calc(digits[:12], w1)
    d2 = calc(digits[:13], w2)
    return digits[12] == str(d1) and digits[13] == str(d2)


@router.get("/cnpj/validate/{cnpj}")
async def validate_cnpj(cnpj: str):
    """Valida CNPJ offline (sem precisar de internet)"""
    valid = validate_cnpj_digits(cnpj)
    return {
        "cnpj": cnpj,
        "valid": valid,
        "message": "CNPJ válido" if valid else "CNPJ inválido"
    }


# ──────────────────────────────────────────────────────────────
# PUBLICAÇÕES (LISTINGS)
# ──────────────────────────────────────────────────────────────

@router.post("/listings")
async def create_listing(
    title: str = Form(...),
    description: str = Form(""),
    crop: str = Form(...),
    quantity_kg: float = Form(...),
    price_per_kg: float = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    """Produtor cria uma publicação de venda"""
    image_path = None
    if image and image.filename:
        ext = image.filename.rsplit(".", 1)[-1].lower()
        if ext not in {"jpg", "jpeg", "png", "webp"}:
            raise HTTPException(400, "Imagem deve ser JPG, PNG ou WEBP")
        filename = f"{uuid4().hex}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        image_path = f"/static/uploads/{filename}"

    result = market_db.create_listing(
        user_id=current_user["user_id"],
        title=title,
        description=description,
        crop=crop,
        quantity_kg=quantity_kg,
        price_per_kg=price_per_kg,
        city=city,
        state=state,
        image_path=image_path
    )
    if not result.get("success"):
        raise HTTPException(500, result.get("error", "Erro ao criar publicação"))
    return {"success": True, "listing_id": result["listing_id"],
            "message": "Publicação criada com sucesso!"}


@router.get("/listings")
async def list_listings(
    state: Optional[str] = None,
    crop: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Lista todas as publicações disponíveis (pode filtrar por estado/cultura)"""
    listings = market_db.get_listings(state=state, crop=crop)
    return {"success": True, "total": len(listings), "listings": listings}


@router.get("/listings/mine")
async def my_listings(current_user: dict = Depends(get_current_user)):
    """Lista publicações do usuário logado"""
    listings = market_db.get_my_listings(current_user["user_id"])
    return {"success": True, "listings": listings}


@router.get("/listings/{listing_id}")
async def get_listing(listing_id: int,
                       current_user: dict = Depends(get_current_user)):
    listing = market_db.get_listing(listing_id)
    if not listing:
        raise HTTPException(404, "Publicação não encontrada")
    return listing


@router.delete("/listings/{listing_id}")
async def delete_listing(listing_id: int,
                          current_user: dict = Depends(get_current_user)):
    deleted = market_db.delete_listing(listing_id, current_user["user_id"])
    if not deleted:
        raise HTTPException(403, "Você não pode remover esta publicação")
    return {"success": True, "message": "Publicação removida"}


# ──────────────────────────────────────────────────────────────
# NEGOCIAÇÕES (DEALS)
# ──────────────────────────────────────────────────────────────

@router.post("/deals")
async def start_deal(data: DealCreate,
                      current_user: dict = Depends(get_current_user)):
    """Comprador inicia negociação com produtor"""
    listing = market_db.get_listing(data.listing_id)
    if not listing:
        raise HTTPException(404, "Publicação não encontrada")
    if listing["status"] != "disponivel":
        raise HTTPException(400, "Esta publicação não está mais disponível")
    if listing["user_id"] == current_user["user_id"]:
        raise HTTPException(400, "Você não pode comprar sua própria publicação")

    result = market_db.create_deal(
        listing_id=data.listing_id,
        buyer_id=current_user["user_id"],
        producer_id=listing["user_id"]
    )
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Erro ao iniciar negociação"))
    return {"success": True, "deal_id": result["deal_id"],
            "message": "Negociação iniciada! Envie uma mensagem para o produtor."}


@router.get("/deals")
async def my_deals(current_user: dict = Depends(get_current_user)):
    """Lista todos os negócios do usuário"""
    deals = market_db.get_my_deals(current_user["user_id"])
    return {"success": True, "deals": deals}


@router.get("/deals/transports")
async def open_transports(current_user: dict = Depends(get_current_user)):
    """Lista negócios fechados que precisam de transportador"""
    transports = market_db.get_open_transports()
    return {"success": True, "transports": transports}


@router.get("/deals/{deal_id}")
async def get_deal(deal_id: int,
                    current_user: dict = Depends(get_current_user)):
    deal = market_db.get_deal(deal_id)
    if not deal:
        raise HTTPException(404, "Negócio não encontrado")
    uid = current_user["user_id"]
    if uid not in (deal["buyer_id"], deal["producer_id"], deal.get("transporter_id")):
        raise HTTPException(403, "Sem permissão para ver este negócio")
    return deal


@router.patch("/deals/{deal_id}/status")
async def update_deal(deal_id: int, data: DealStatusUpdate,
                       current_user: dict = Depends(get_current_user)):
    """
    Atualiza status do negócio.
    - produtor pode: aceitar → 'fechado' | recusar → 'recusado'
    - transportador pode: assumir → 'em_transporte'
    - produtor/comprador: concluir → 'concluido'
    """
    deal = market_db.get_deal(deal_id)
    if not deal:
        raise HTTPException(404, "Negócio não encontrado")

    uid = current_user["user_id"]
    valid_statuses = {"fechado", "recusado", "cancelado", "em_transporte", "concluido", "negociando"}
    if data.status not in valid_statuses:
        raise HTTPException(400, f"Status inválido. Use: {', '.join(valid_statuses)}")

    result = market_db.update_deal_status(
        deal_id, data.status,
        transport_fee=data.transport_fee,
        transporter_id=data.transporter_id or (uid if data.status == "em_transporte" else None)
    )

    # Se negócio fechado, marca a publicação como vendido
    if data.status == "fechado":
        market_db.update_listing_status(deal["listing_id"], "vendido")

    if not result.get("success"):
        raise HTTPException(500, "Erro ao atualizar status")

    status_labels = {
        "fechado": "Negócio fechado! O produtor aceitou.",
        "recusado": "Negócio recusado.",
        "cancelado": "Negócio cancelado.",
        "em_transporte": "Você assumiu o transporte!",
        "concluido": "Negócio concluído com sucesso!",
        "negociando": "Voltou para negociação."
    }
    return {"success": True, "message": status_labels.get(data.status, "Status atualizado")}


# ──────────────────────────────────────────────────────────────
# MENSAGENS (CHAT INTERNO — OFFLINE)
# ──────────────────────────────────────────────────────────────

@router.post("/messages")
async def send_message(data: MessageSend,
                        current_user: dict = Depends(get_current_user)):
    result = market_db.send_message(
        sender_id=current_user["user_id"],
        receiver_id=data.receiver_id,
        content=data.content,
        deal_id=data.deal_id
    )
    if not result.get("success"):
        raise HTTPException(500, "Erro ao enviar mensagem")
    return {"success": True, "message_id": result["message_id"]}


@router.get("/messages/inbox")
async def get_inbox(current_user: dict = Depends(get_current_user)):
    inbox = market_db.get_inbox(current_user["user_id"])
    unread = market_db.count_unread(current_user["user_id"])
    return {"success": True, "inbox": inbox, "unread_total": unread}


@router.get("/messages/deal/{deal_id}")
async def get_deal_messages(deal_id: int,
                              current_user: dict = Depends(get_current_user)):
    deal = market_db.get_deal(deal_id)
    if not deal:
        raise HTTPException(404, "Negócio não encontrado")
    uid = current_user["user_id"]
    if uid not in (deal["buyer_id"], deal["producer_id"], deal.get("transporter_id")):
        raise HTTPException(403, "Sem permissão")
    market_db.mark_messages_read(uid, deal_id)
    msgs = market_db.get_conversation(0, 0, deal_id=deal_id)
    return {"success": True, "messages": msgs, "deal": deal}


@router.get("/messages/unread")
async def unread_count(current_user: dict = Depends(get_current_user)):
    count = market_db.count_unread(current_user["user_id"])
    return {"unread": count}
