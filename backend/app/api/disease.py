from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.ai_service import ai_service
from app.schemas import DiseaseAnalysisResponse

router = APIRouter(prefix="/disease-detection", tags=["AI Disease Detection Service"])

@router.post("/analyze", response_model=DiseaseAnalysisResponse)
async def analyze_frame_disease(
    file: Optional[UploadFile] = File(None),
    sample_condition: Optional[str] = Form(None)
):
    """
    Accepts hive frame image (or sample tag) and executes MobileNet image classification:
    Returns condition:
    - Healthy Brood
    - Varroa Mite Infestation
    - American Foulbrood
    with confidence score, plain-language advisory, and recommended action.
    """
    filename = ""
    image_bytes = b""
    if file:
        filename = file.filename
        image_bytes = await file.read()
    elif sample_condition:
        filename = f"{sample_condition}.jpg"

    result = ai_service.analyze_hive_frame_image(image_bytes=image_bytes, filename=filename)

    return DiseaseAnalysisResponse(
        detected_condition=result["detected_condition"],
        confidence_score=result["confidence_score"],
        severity=result["severity"],
        plain_language_explanation=result["plain_language_explanation"],
        recommended_action=result["recommended_action"],
        kvic_helpline=result["kvic_helpline"]
    )
