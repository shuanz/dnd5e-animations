import json
from deep_translator import DeeplTranslator
import os

def translate_with_deepl(api_key, text, source='en', target='pt'):
    """
    Traduz um texto usando a API do DeepL
    """
    try:
        translated = DeeplTranslator(
            api_key=api_key,
            source=source,
            target=target,
            use_free_api=True
        ).translate(text)
        return translated
    except Exception as e:
        print(f"Erro ao traduzir '{text}': {str(e)}")
        return None

def process_json_file(input_file, output_file, api_key):
    # Carrega o arquivo de entrada
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Analisando o arquivo...")
    
    # Função para processar e duplicar itens com tradução
    def process_and_duplicate(data):
        if isinstance(data, dict):
            # Se for um dicionário com 'label', duplica com a tradução
            if 'label' in data and isinstance(data['label'], str):
                # Cria uma cópia do item original
                translated_item = data.copy()
                
                # Traduz o label
                original_label = data['label']
                print(f"Traduzindo: {original_label}")
                translated_label = translate_with_deepl(api_key, original_label)
                
                if translated_label:
                    # Atualiza o label no item traduzido
                    translated_item['label'] = f"{original_label} ({translated_label})"
                    
                    # Retorna ambos: o original e o traduzido
                    return [data, translated_item]
            
            # Processa os valores do dicionário
            new_dict = {}
            for key, value in data.items():
                processed = process_and_duplicate(value)
                if processed is not None:
                    new_dict[key] = processed
                else:
                    new_dict[key] = value
            return new_dict
            
        elif isinstance(data, list):
            new_list = []
            for item in data:
                processed = process_and_duplicate(item)
                if isinstance(processed, list):
                    new_list.extend(processed)
                else:
                    new_list.append(processed)
            return new_list
        
        return data
    
    print("Iniciando a duplicação com traduções...")
    result = process_and_duplicate(data)
    
    # Salva o resultado
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
    
    print(f"\nProcesso concluído! Resultado salvo em {output_file}")

if __name__ == "__main__":
    # Configurações
    DEEPL_API_KEY = "bc2d3402-a4f1-44e7-8341-c783bd22720f:fx"  # Sua chave de API
    INPUT_FILE = "module/autorec.json"
    OUTPUT_FILE = "module/autorec_duplicated.json"
    
    if not DEEPL_API_KEY or DEEPL_API_KEY == "SUA_CHAVE_DE_API_DEEPL":
        print("ERRO: Por favor, adicione sua chave de API do DeepL no código.")
        print("Você pode obter uma em: https://www.deepl.com/pro#developer")
    else:
        process_json_file(INPUT_FILE, OUTPUT_FILE, DEEPL_API_KEY)
