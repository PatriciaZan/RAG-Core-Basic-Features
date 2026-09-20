## `run_chunking.py` é a versão mais recente e com mais opções para chunking.
Realiza o chunking de arquivos `.md` e `.txt` preferencialmente email.  
Possui as opções de:
- 1 - Processar TODOS os arquivos da pasta /data
- 2 - Processar UM arquivo específico (informar o nome) com extensão .md ou .txt
- 3 - Processar por TIPO de arquivo (.md ou .txt)

Após a localização dos arquivos a opção de seleção de sensibilidade ficará disponível:
- 1 - publico
- 2 - interno
- 3 - restrito

Os arquivos são salvos na pasta `output_chunking` na raiz do projeto.  

Os arquivos de .md (markdown) são processados com a seguinte schema (exemplo):
```json
{
    "source_file": "2026-01-architecture_review_db.md",
    "doc_sensitivity": "interno",
    "doc_type": "2026-01-architecture_review_db",
    "doc_extension": ".md",
    "resultado": [
        {
            "texto": "",
            "metadata": {
                "sensitivity": "interno",
                "chunk_index": 0,
                "total_chunks": 2,
                "chunk_id": "2f34dc756e03420e8a84e4d01444edc0",
                "file_name": "2026-01-architecture_review_db.md",
                "section_index": 0,
                "h1": "Ata de Reunião: Arquitetura de Banco de Dados e Cache Redis"
            }
        }
     ]
}
```
E os arquivos .txt(email) são processados com a seguinte schema(exemplo):
```json
{
  "source_file": "customer_001_sincronizacao.txt",
  "doc_sensitivity": "restrito",
  "doc_type": "customer_001_sincronizacao",
  "doc_extension": ".txt",
  "resultado": [
    {
      "texto": "",
      "metadata": {
        "sensitivity": "restrito",
        "chunk_index": 0,
        "total_chunks": 2,
        "chunk_id": "e4a63178a24f41f785985768de9f1243",
        "file_name": "customer_001_sincronizacao.txt",
        "remetente": "gerencia@boacompra.com.br",
        "destinatario": "@vendefacil.com.br, @vendefacil.com.br",
        "assunto": "URGENTE: Falha grave de sincronização - Ticket TCK-1001",
        "data": "10 de Fevereiro de 2026 09:15",
        "ticket_id": "TCK-1001"
      }
    }
  ]
}

```
---

## `run_chunking_v1.py` é a versão mais "simples" de chunking.
**Apenas para salvar o script, não é recomendado usar, pois os schemas gerados são imcompletos.**
Irá processar todos os arquivos contidos na pasta /data com as extensões .md ou .txt.  
Possibilitando escolher a sensibilidade da cada arquivo separadamente:
- 1 - publico
- 2 - interno
- 3 - restrito

Os arquivos são salvos na pasta `output_chunking` na raiz do projeto.  