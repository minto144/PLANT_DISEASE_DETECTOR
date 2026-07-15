"""
classes.py — Disease class labels + treatment recommendations.
Class names match the EXACT folder names in your PlantVillage dataset.
"""

# Exactly 15 classes — matches your dataset folder names
CLASS_LABELS = [
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite",
    "Tomato__Target_Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus",
    "Tomato__Tomato_mosaic_virus",
    "Tomato_healthy",
]

DISEASE_INFO = {
    "Pepper__bell___Bacterial_spot": {
        "name": "Pepper Bacterial Spot",
        "plant": "Bell Pepper",
        "severity": "moderate",
        "symptoms": "Small water-soaked circular spots with yellow halos on leaves.",
        "treatment": "Copper-based bactericides. Remove infected plant material.",
        "prevention": "Use disease-free seed. Rotate crops every 2–3 years.",
    },
    "Pepper__bell___healthy": {
        "name": "Healthy Bell Pepper",
        "plant": "Bell Pepper",
        "severity": "none",
        "symptoms": "No disease detected.",
        "treatment": "No treatment needed.",
        "prevention": "Adequate spacing and drip irrigation reduce disease risk.",
    },
    "Potato___Early_blight": {
        "name": "Potato Early Blight",
        "plant": "Potato",
        "severity": "moderate",
        "symptoms": "Dark brown spots with concentric rings (target pattern) on older leaves.",
        "treatment": "Apply chlorothalonil, mancozeb, or azoxystrobin fungicides.",
        "prevention": "Rotate crops. Avoid wetting foliage. Destroy crop debris.",
    },
    "Potato___Late_blight": {
        "name": "Potato Late Blight",
        "plant": "Potato",
        "severity": "critical",
        "symptoms": "Water-soaked dark green lesions that turn brown; white mold on underside.",
        "treatment": "Apply metalaxyl + mancozeb or cymoxanil immediately. Destroy infected plants.",
        "prevention": "Use certified seed potatoes. Avoid overhead watering. Monitor humidity.",
    },
    "Potato___healthy": {
        "name": "Healthy Potato Leaf",
        "plant": "Potato",
        "severity": "none",
        "symptoms": "No disease detected.",
        "treatment": "No treatment needed.",
        "prevention": "Use certified disease-free seed tubers.",
    },
    "Tomato_Bacterial_spot": {
        "name": "Tomato Bacterial Spot",
        "plant": "Tomato",
        "severity": "moderate",
        "symptoms": "Small water-soaked circular spots with yellow halos; rough scabby lesions on fruit.",
        "treatment": "Copper hydroxide + mancozeb sprays. Remove infected leaves.",
        "prevention": "Use disease-free seed. Avoid working in wet plants.",
    },
    "Tomato_Early_blight": {
        "name": "Tomato Early Blight",
        "plant": "Tomato",
        "severity": "moderate",
        "symptoms": "Dark brown spots with concentric rings starting on lower leaves.",
        "treatment": "Apply chlorothalonil or mancozeb. Remove lower infected leaves.",
        "prevention": "Crop rotation. Mulch soil to reduce splash dispersal.",
    },
    "Tomato_Late_blight": {
        "name": "Tomato Late Blight",
        "plant": "Tomato",
        "severity": "critical",
        "symptoms": "Large irregular water-soaked greasy-looking lesions. White fuzzy growth underneath.",
        "treatment": "Apply metalaxyl or cymoxanil immediately. Destroy infected plants.",
        "prevention": "Avoid overhead irrigation. Scout regularly in humid conditions.",
    },
    "Tomato_Leaf_Mold": {
        "name": "Tomato Leaf Mold",
        "plant": "Tomato",
        "severity": "moderate",
        "symptoms": "Pale green to yellow patches on upper surface; olive-green mold below.",
        "treatment": "Improve ventilation. Apply chlorothalonil or mancozeb.",
        "prevention": "Reduce humidity in greenhouses. Use resistant varieties.",
    },
    "Tomato_Septoria_leaf_spot": {
        "name": "Tomato Septoria Leaf Spot",
        "plant": "Tomato",
        "severity": "moderate",
        "symptoms": "Many small circular spots with dark borders and light centers.",
        "treatment": "Remove lower leaves. Apply mancozeb or chlorothalonil.",
        "prevention": "Mulch to prevent soil splash. Avoid overhead watering.",
    },
    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "name": "Tomato Spider Mites",
        "plant": "Tomato",
        "severity": "moderate",
        "symptoms": "Fine stippling, bronzing of leaves; tiny webs on underside.",
        "treatment": "Apply miticide (abamectin, bifenazate) or neem oil. Spray undersides of leaves.",
        "prevention": "Keep plants well-watered. Avoid dusty, hot conditions.",
    },
    "Tomato__Target_Spot": {
        "name": "Tomato Target Spot",
        "plant": "Tomato",
        "severity": "moderate",
        "symptoms": "Circular brown spots with concentric rings on leaves and fruit.",
        "treatment": "Apply fungicides (azoxystrobin, difenoconazole).",
        "prevention": "Crop rotation. Remove debris. Good air circulation.",
    },
    "Tomato__Tomato_YellowLeaf__Curl_Virus": {
        "name": "Tomato Yellow Leaf Curl Virus",
        "plant": "Tomato",
        "severity": "critical",
        "symptoms": "Upward leaf curling, yellowing leaf margins, stunted plant.",
        "treatment": "No cure. Remove and destroy infected plants immediately.",
        "prevention": "Control whitefly (virus vector) with insecticides or reflective mulch. Use resistant varieties.",
    },
    "Tomato__Tomato_mosaic_virus": {
        "name": "Tomato Mosaic Virus",
        "plant": "Tomato",
        "severity": "high",
        "symptoms": "Mosaic light/dark green pattern; distorted or fern-like leaves.",
        "treatment": "No cure. Remove infected plants. Disinfect tools.",
        "prevention": "Wash hands before handling plants. Avoid tobacco near plants. Use resistant varieties.",
    },
    "Tomato_healthy": {
        "name": "Healthy Tomato Leaf",
        "plant": "Tomato",
        "severity": "none",
        "symptoms": "No disease detected.",
        "treatment": "No treatment needed.",
        "prevention": "Maintain consistent watering, staking, and nutrition.",
    },
}

SEVERITY_COLOR = {
    "none":     "#22c55e",
    "moderate": "#f59e0b",
    "high":     "#ef4444",
    "critical": "#7c3aed",
}


def get_disease_info(class_label: str) -> dict:
    info = DISEASE_INFO.get(class_label)
    if not info:
        return {
            "name": class_label.replace("__", " ").replace("_", " ").strip(),
            "plant": "Unknown",
            "severity": "unknown",
            "symptoms": "No data available.",
            "treatment": "Consult a local agricultural extension officer.",
            "prevention": "Monitor your crop regularly.",
        }
    return info