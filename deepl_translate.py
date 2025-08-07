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
            use_free_api=True  # Use False se estiver usando a API paga
        ).translate(text)
        return translated
    except Exception as e:
        print(f"Erro ao traduzir '{text}': {str(e)}")
        return None

def process_json_file(input_file, output_file, api_key):
    # Verifica se o arquivo de saída já existe
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Arquivo {output_file} carregado. Continuando traduções...")
    else:
        # Se o arquivo de saída não existir, carrega o arquivo de entrada
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Novo arquivo criado a partir de {input_file}")
    
    # Conta quantos labels precisam ser traduzidos
    total_labels = sum(1 for _ in json.dumps(data).split('"label":')) - 1
    translated_count = 0
    needs_translation = 0
    
    # Primeiro, conta quantos precisam de tradução
    def count_needs_translation(d):
        nonlocal needs_translation
        if isinstance(d, dict):
            if 'label' in d and 'label_pt_br' not in d and isinstance(d['label'], str):
                needs_translation += 1
            for value in d.values():
                if isinstance(value, (dict, list)):
                    count_needs_translation(value)
        elif isinstance(d, list):
            for item in d:
                if isinstance(item, (dict, list)):
                    count_needs_translation(item)
    
    print("Analisando o arquivo...")
    count_needs_translation(data)
    print(f"Total de labels: {total_labels}")
    print(f"Labels que precisam de tradução: {needs_translation}")
    
    if needs_translation == 0:
        print("Nenhuma tradução necessária!")
        return
    
    # Função para adicionar traduções
    def add_translations(d, api_key):
        nonlocal translated_count
        if isinstance(d, dict):
            if 'label' in d and 'label_pt_br' not in d and isinstance(d['label'], str):
                label = d['label']
                translated_count += 1
                print(f"[{translated_count}/{needs_translation}] Traduzindo: {label}")
                
                translated = translate_with_deepl(api_key, label)
                if translated:
                    d['label_pt_br'] = translated
                    print(f"   → {translated}")
                    
                    # Salva o progresso a cada 10 traduções
                    if translated_count % 10 == 0:
                        save_progress()
                
            for value in d.values():
                if isinstance(value, (dict, list)):
                    add_translations(value, api_key)
        elif isinstance(d, list):
            for item in d:
                if isinstance(item, (dict, list)):
                    add_translations(item, api_key)
    
    # Função para salvar o progresso
    def save_progress():
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"Progresso salvo: {translated_count}/{needs_translation} traduções")
    
    # Inicia o processo de tradução
    print("\nIniciando as traduções...")
    add_translations(data, api_key)
    
    # Salva o resultado final
    save_progress()
    print("\nTradução concluída!")

if __name__ == "__main__":
    # Configurações
    DEEPL_API_KEY = "bc2d3402-a4f1-44e7-8341-c783bd22720f:fx"  # Substitua pela sua chave de API
    INPUT_FILE = "module/autorec.json"
    OUTPUT_FILE = "module/autorec_pt_br.json"
    
    if not DEEPL_API_KEY or DEEPL_API_KEY == "SUA_CHAVE_DE_API_DEEPL":
        print("ERRO: Por favor, adicione sua chave de API do DeepL no código.")
        print("Você pode obter uma em: https://www.deepl.com/pro#developer")
    else:
        process_json_file(INPUT_FILE, OUTPUT_FILE, DEEPL_API_KEY)
