import os
import base64
import json
import re
import google.generativeai as genai
from PIL import Image
import io
import datetime
from dotenv import load_dotenv

try:
    load_dotenv()
    AI_API_KEY = os.getenv("AI_API_KEY")
except KeyError:
    print("AVISO: Chave da API do Google não encontrada na variável de ambiente 'AI_API_KEY'.")


genai.configure(api_key=AI_API_KEY)

VALIDATION_SCORE_THRESHOLD = 0.7  
NAME_MATCH_THRESHOLD = 0.8

def calculate_name_similarity(name1, name2):
    """Calcula a similaridade entre dois nomes (0 a 1) usando Jaccard."""
    if not name1 or not name2:
        return 0.0
    words1 = set(name1.lower().split())
    words2 = set(name2.lower().split())
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    return float(intersection) / union if union > 0 else 0.0

def clean_json_response(text):
    """Remove possíveis marcadores de markdown (```json ... ```) da resposta."""
    match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text.strip()

def validate_document(document_base64, doc_type, user_info=None):


    """
    Valida um documento usando a API Gemini do Google (modelo multimodal).

    Args:
        document_base64: String da imagem/documento codificada em Base64.
        doc_type: Tipo de documento (ex: "RG", "CPF", "CNH").
        user_info: Dicionário com informações do usuário para verificação cruzada.

    Returns:
        Dicionário com os resultados da validação ou informações de erro.
    """
    # Preparar o prompt
    prompt_parts = [f"Este é um documento do tipo {doc_type} para fins de verificação. "]

    if user_info:
        prompt_parts.append("Por favor, verifique se as seguintes informações correspondem ao que está no documento: ")
        for key, value in user_info.items():
            prompt_parts.append(f"{key}: {value}, ")

    prompt_parts.append(
        "Analise este documento cuidadosamente e extraia as seguintes informações: "
        "1. Tipo de documento (confirme se é o tipo declarado). "
        "2. Nome completo no documento. "
        "3. Número/ID do documento. "
        "4. Data de emissão ou data de validade (se visível). "
        "5. Uma pontuação de validação de 0.0 a 1.0 indicando sua confiança de que este é um documento genuíno. "
        "6. Quaisquer sinais de adulteração ou fraude. "
        "Retorne os resultados estritamente em formato JSON com as chaves: document_type, full_name, document_number, date, "
        "validation_score, potential_fraud (boolean), e reasoning (string)."
    )
    final_prompt = "".join(prompt_parts)

    # Preparar a imagem
    try:
        image_bytes = base64.b64decode(document_base64)
        img = Image.open(io.BytesIO(image_bytes))

    except base64.binascii.Error as b64_error:
        print(f"Erro ao decodificar Base64: {b64_error}")
        return {
            "error": f"Imagem Base64 inválida: {b64_error}",
            "validation_score": 0.0, "potential_fraud": True,
            "reasoning": "Falha ao processar a imagem fornecida (Base64 inválido)."
        }
    except Exception as img_error:
        print(f"Erro ao abrir imagem: {img_error}")
        return {
            "error": f"Erro ao processar imagem: {img_error}",
            "validation_score": 0.0, "potential_fraud": True,
            "reasoning": "Falha ao processar a imagem fornecida."
        }

    model = genai.GenerativeModel('gemini-1.5-flash')

    generation_config = genai.types.GenerationConfig(
        response_mime_type="application/json"
    )

    try:
        response = model.generate_content([final_prompt, img], generation_config=generation_config)

        raw_json_text = response.text
        cleaned_json_text = clean_json_response(raw_json_text)
        result = json.loads(cleaned_json_text)

        result['timestamp'] = datetime.datetime.now().isoformat()

        # Verificar correspondência de nome se user_info foi fornecido
        if user_info and 'full_name' in user_info and 'full_name' in result and result['full_name']:
            name_match = calculate_name_similarity(user_info['full_name'], result['full_name'])
            result['name_match_score'] = name_match
            result['name_verified'] = name_match >= NAME_MATCH_THRESHOLD
        elif user_info and 'full_name' in user_info:
             result['name_verified'] = False

        # Garantir que as chaves esperadas existam, mesmo que vazias/padrão
        result.setdefault('document_type', None)
        result.setdefault('full_name', None)
        result.setdefault('document_number', None)
        result.setdefault('date', None)
        result.setdefault('validation_score', 0.0)
        result.setdefault('potential_fraud', True)
        result.setdefault('reasoning', 'N/A')

        return result

    except json.JSONDecodeError as json_err:
        print(f"Erro ao decodificar JSON da API Gemini: {json_err}")
        print(f"Resposta recebida (raw): {raw_json_text}")
        return {
            "error": f"Falha ao decodificar resposta JSON da API: {json_err}",
            "raw_response": raw_json_text,
            "validation_score": 0.0, "potential_fraud": True,
            "reasoning": "A API não retornou um JSON válido."
        }
    except Exception as e:
        # Captura outros erros da API Gemini (ex: cota excedida, erro de autenticação)
        print(f"Erro durante a chamada da API Gemini: {e}")
        error_details = str(e)
        if hasattr(e, 'message'):
             error_details = e.message

        return {
            "error": f"Erro na API Gemini: {error_details}",
            "validation_score": 0.0, "potential_fraud": True,
            "reasoning": "Erro ocorreu durante a validação via API."
        }

def validate_esports_profile(profile_url, platform, username=None):
    """
    Valida um perfil de e-sports usando a API Gemini (modelo de texto).

    Args:
        profile_url: URL do perfil.
        platform: Nome da plataforma (Steam, Battlenet, etc.).
        username: Nome de usuário (opcional).

    Returns:
        Dicionário com resultados da validação ou erro.
    """
    prompt = (f"Estou verificando se este perfil da plataforma {platform} ({profile_url}) "
              f"pertence a alguém genuinamente interessado em e-sports. "
              f"O nome de usuário do perfil é: {username if username else 'desconhecido'}. "
              "Por favor, analise a URL (sem acessá-la diretamente, apenas com base no formato e contexto) e forneça as seguintes informações: "
              "1. Verifique se esta parece ser uma URL válida para um perfil na plataforma {platform}. "
              "2. Indique quão relevante este perfil parece ser para e-sports (escala 0.0 a 1.0). "
              "3. Extraia quaisquer times ou jogos de e-sports mencionados explicitamente no nome de usuário ou URL, se houver. "
              "4. Procure por quaisquer sinais suspeitos óbvios na URL ou nome de usuário. "
              "Retorne os resultados estritamente em formato JSON com as chaves: is_valid_url_format (boolean), relevance_score (float), "
              "esports_elements (list of strings), suspicious_elements (list of strings).")

    model = genai.GenerativeModel('gemini-pro')  # Modelo de texto do Gemini

    generation_config = genai.types.GenerationConfig(
        response_mime_type="application/json"
    )

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        raw_json_text = response.text
        cleaned_json_text = clean_json_response(raw_json_text)
        result = json.loads(cleaned_json_text)

        result.setdefault('is_valid_url_format', bool(re.match(r'^https?://', profile_url))) # Verificação básica
        result.setdefault('relevance_score', 0.0)
        result.setdefault('esports_elements', [])
        result.setdefault('suspicious_elements', [])

        return result

    except json.JSONDecodeError as json_err:
        print(f"Erro ao decodificar JSON da API Gemini (eSports): {json_err}")
        print(f"Resposta recebida (raw): {raw_json_text}")
        return {
            "error": f"Falha ao decodificar resposta JSON da API: {json_err}", "raw_response": raw_json_text,
            "is_valid_url_format": False, "relevance_score": 0.0, "esports_elements": [],
            "suspicious_elements": ["Falha na análise do perfil (JSON inválido)"]
        }
    except Exception as e:
        print(f"Erro durante a chamada da API Gemini (eSports): {e}")
        error_details = str(e)
        if hasattr(e, 'message'):
            error_details = e.message
        return {
            "error": f"Erro na API Gemini: {error_details}",
            "is_valid_url_format": False, "relevance_score": 0.0, "esports_elements": [],
            "suspicious_elements": ["Falha na análise do perfil (Erro na API)"]
        }

def analyze_social_media(platform_data, platform):
    """
    Analyze social media data to identify esports-related interests.

    Args:
        platform_data: Dictionary with social media data
        platform: Platform name (twitter, facebook, etc.)

    Returns:
        Dictionary with analysis results
    """
    prompt = (f"Analyze this {platform} profile data to identify esports-related interests, "
              f"teams followed, and general level of engagement with esports content. "
              f"Here's the data: {json.dumps(platform_data)}. "
              "Provide: "
              "1. (esports_engagement_score) An esports_engagement_score from 0.0 to 1.0 "
              "2. (teams) List of identified esports teams or brands the user follows/interacts with "
              "3. (games) List of esports games the user shows interest in "
              "4. (authenticity_assessment) Overall assessment of this user's authenticity as an esports fan "
              "Return results in JSON format.")

    model = genai.GenerativeModel('gemini-1.5-flash')

    generation_config = genai.types.GenerationConfig(
        response_mime_type="application/json"
    )

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        raw_json_text = response.text
        cleaned_json_text = clean_json_response(raw_json_text)
        return json.loads(cleaned_json_text)

    except json.JSONDecodeError as json_err:
        print(f"Erro ao decodificar JSON da API Gemini (análise social): {json_err}")
        print(f"Resposta recebida (raw): {raw_json_text}")
        return {
            "error": f"Falha ao decodificar resposta JSON da API: {json_err}",
            "esports_engagement_score": 0.0,
            "teams": [],
            "games": [],
            "authenticity_assessment": "Could not analyze profile data (JSON inválido)"
        }
    except Exception as e:
        print(f"Erro durante a chamada da API Gemini (análise social): {e}")
        error_details = str(e)
        if hasattr(e, 'message'):
            error_details = e.message
        return {
            "error": f"Erro na API Gemini: {error_details}",
            "esports_engagement_score": 0.0,
            "teams": [],
            "games": [],
            "authenticity_assessment": "Could not analyze profile data (Erro na API)"
        }

def calculate_name_similarity(name1, name2):
    """Simple function to calculate name similarity between 0 and 1."""
    # Convert to lowercase and split into words
    words1 = set(name1.lower().split())
    words2 = set(name2.lower().split())

    # Calculate Jaccard similarity
    if not words1 or not words2:
        return 0.0

    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    return intersection / union if union > 0 else 0.0

def clean_json_response(text):
    """
    Tenta limpar uma string que se assemelha a JSON removendo caracteres extras
    antes e depois do objeto JSON principal.
    """
    try:
        # Tenta carregar diretamente
        return json.dumps(json.loads(text))
    except json.JSONDecodeError:
        start_index = text.find('{')
        end_index = text.rfind('}')
        if start_index != -1 and end_index != -1 and start_index < end_index:
            cleaned_text = text[start_index:end_index + 1]
            try:
                return json.dumps(json.loads(cleaned_text))
            except json.JSONDecodeError:
                return "{}"  # Retorna um JSON vazio em caso de falha
        else:
            return "{}"
