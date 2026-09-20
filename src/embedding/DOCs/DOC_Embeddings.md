## `generate_embeddings.py` - Aqui é a Chamada para realizar os embeddings
1. Faz a leitura dos arquivos da pasta `output_chunking` e percorre os arquivos.
2. Possibilita a escolha do usuário entre:
   - [ok] - Prosseguir com a geração de embeddings para este arquivo
   - [pular] - Pular este arquivo e ir para o próximo
   - [exit] - Parar completamente a execução
3. Faz a chamada da função `add_embeddings_to_json` para construir os embeddings

---

## `add_embeddings_to_json.py` Executa a chamada de embeddings e salva novo json
1. Faz a leitura do arquivo .json recebido
2. Chama a função `get_embeddings` para a geração dos embeddings para cada chunks
3. Salva novo arquivo .json em `output_embeddings` na raiz do projeto

---

## `get_embeddings`  Responsovél por gerar embeddings
1. Conecta com o OPENROUTER
2. Realiza o embedding do chunk recebido