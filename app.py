import openai
import os
from dotenv import load_dotenv
import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from io import BytesIO
from flask import Flask, render_template, request, jsonify

# Charger la clé API OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Erreur : La clé API OpenAI n'est pas définie dans l'environnement")
    exit()

openai.api_key = api_key

# Liste de slogans prédéfinis
slogans_predefinis = [
    "Révolution numérique", "Innovation pour tous", "Codez votre avenir",
    "Eat The Rich", "Tech for good", "Construisons ensemble",
    "we are anonymous", "Créer. Innover. Transformer.", "Expect Us"
]

# Fonction de génération du logo avec DALL·E
def generer_logo_dalle(nom_dev, slogan, texte_nom_color, texte_slogan_color, font_choice, sortie="logo_dalle.png"):
    prompt = f"Scène ultra-réaliste d'une manifestation nocturne en France, sous tension. Des Black Blocs vêtus de noir, cagoulés, forment une barricade en feu, brandissant des fumigènes rouges et des drapeaux anarchistes. En fond, une banque saccagée, vitrines brisées, un fast-food vandalisé, un véhicule en flammes illuminant la scène. Des tags lisibles sur les murs : 'ACAB', 'No Justice, No Peace', 'Révolte Populaire'. Gaz lacrymogène et fumée noire flottent dans l'air. En face, des CRS en armure avancent en formation, boucliers luisant sous les gyrophares bleus. Le contraste entre la lumière orangée des flammes et le bleu des sirènes crée une ambiance cinématographique sombre et immersive. Détails réalistes : pluie ruisselant sur les casques, étincelles des barricades, vêtements usés, regards tendus, tensions palpables. Aucun texte aléatoire. Scène brute et percutante."

    try:
        response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
        image_url = response["data"][0]["url"]
        img_data = requests.get(image_url).content
        image = Image.open(BytesIO(img_data))

        # Appliquer les effets glitch + contraste
        image = appliquer_effets(image)

        # Ajouter le texte avec couleurs et effets
        image = ajouter_texte_personnalise(image, nom_dev, slogan, texte_nom_color, texte_slogan_color, font_choice)

        # Sauvegarder l'image générée
        image.save(sortie)
        print(f"✅ Logo généré avec succès : {sortie}")
    except Exception as e:
        print(f"❌ Erreur OpenAI : {e}")

# Appliquer des effets glitch et augmenter le contraste
def appliquer_effets(image):
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.8)
    image = image.filter(ImageFilter.GaussianBlur(0.5))
    return image

# Ajouter un texte personnalisé avec contour lumineux et couleurs choisies
def ajouter_texte_personnalise(image, nom, slogan, texte_nom_color, texte_slogan_color, font_choice):
    image = image.convert("RGB")
    draw = ImageDraw.Draw(image)

    try:
        # Choisir la police en fonction de la sélection
        font_path = os.path.join("uploads", font_choice)
        font = ImageFont.truetype(font_path, 150)
    except IOError:
        print("❌ Police non trouvée, utilisation d'une police système")
        font = ImageFont.load_default()

    # Ajouter le texte pour le nom
    text_bbox = draw.textbbox((0, 0), nom, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position_nom = ((image.width - text_width) // 2, (image.height - text_height) // 4)

    # Ajouter un contour lumineux
    contour_color = (255, 255, 255)
    for offset in range(-5, 6, 2):
        draw.text((position_nom[0] + offset, position_nom[1] + offset), nom, font=font, fill=contour_color)

    # Ajouter le texte central
    draw.text(position_nom, nom, font=font, fill=texte_nom_color)

    # Ajouter le texte pour le slogan sous le nom
    text_bbox_slogan = draw.textbbox((0, 0), slogan, font=font)
    text_width_slogan = text_bbox_slogan[2] - text_bbox_slogan[0]
    text_height_slogan = text_bbox_slogan[3] - text_bbox_slogan[1]
    position_slogan = ((image.width - text_width_slogan) // 2, (image.height - text_height_slogan) // 1.5)

    # Ajouter un contour lumineux pour le slogan
    for offset in range(-5, 6, 2):
        draw.text((position_slogan[0] + offset, position_slogan[1] + offset), slogan, font=font, fill=contour_color)

    # Ajouter le texte du slogan avec la couleur choisie
    draw.text(position_slogan, slogan, font=font, fill=texte_slogan_color)

    return image

# Setup de Flask
app = Flask(__name__)

# Page d'accueil avec formulaire pour personnalisation
@app.route('/')
def index():
    # Récupérer les polices dans le dossier "uploads"
    polices = [f for f in os.listdir('uploads') if f.endswith('.ttf')]
    return render_template('index.html', polices=polices, slogans=slogans_predefinis)

# Générer l'image en fonction des choix de l'utilisateur
@app.route('/generate', methods=['POST'])
def generate():
    # Récupérer les données du formulaire
    nom_dev = request.form.get('nom_dev')
    slogan = request.form.get('slogan')
    custom_slogan = request.form.get('custom_slogan')  # Récupérer le slogan personnalisé

    # Si un slogan personnalisé est entré, on l'utilise, sinon on garde celui de la liste
    if custom_slogan:
        slogan = custom_slogan

    texte_nom_color = request.form.get('texte_nom_color')
    texte_slogan_color = request.form.get('texte_slogan_color')
    font_choice = request.form.get('font_choice')

    # Vérifier si des champs nécessaires sont manquants
    if not nom_dev or not slogan or not texte_nom_color or not texte_slogan_color or not font_choice:
        return jsonify({"error": "Tous les champs sont requis!"}), 400

    # Générer le logo avec les paramètres donnés
    try:
        output_file = 'static/logo_dalle.png'  # Sauvegarder l'image dans le dossier static
        generer_logo_dalle(nom_dev, slogan, texte_nom_color, texte_slogan_color, font_choice, sortie=output_file)

        # Renvoyer la réponse avec l'URL de l'image
        return render_template('index.html',
                               polices=os.listdir('uploads'),
                               slogans=slogans_predefinis,
                               image_url=output_file,
                               custom_slogan=custom_slogan)  # Ajouter custom_slogan au template

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la génération du logo : {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
