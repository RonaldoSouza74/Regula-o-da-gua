# Regulação da Água

Artigo científico sobre **restrições hidráulicas operativas no Sistema Interligado Nacional (SIN)**, com panorama por bacia (São Francisco, Paraná, Grande, Paranaíba, Paranapanema, Iguaçu, Uruguai, Tocantins, Paraíba do Sul e bacias amazônicas), arcabouço institucional (ANA, IBAMA, ONS, ANEEL, MME/CMSE, TCU) e estudo aprofundado dos **hidrogramas da UHE Belo Monte** e de sua flexibilização.

## Conteúdo

| Caminho | Descrição |
|:--|:--|
| `artigo/Artigo_Restricoes_Hidraulicas_SIN_Belo_Monte.docx` | Artigo completo (≈ 15.400 palavras de texto corrido, 8 quadros, 6 figuras, referências em ABNT autor-data) |
| `artigo/Artigo_Restricoes_Hidraulicas_SIN_Belo_Monte.pdf` | Mesma versão em PDF |
| `artigo/fonte/` | Texto-fonte em Markdown (`parte01.md` … `parte07.md`) e `artigo_completo.md` |
| `artigo/figuras/` | Figuras em PNG (capacidade hidrelétrica 2015 × atual, regularização, vazões mínimas por bacia, hidrogramas, geração simulada, alavancas) |
| `artigo/analise/modelo_hidrograma.py` | Balanço hídrico mensal de Belo Monte (hidrogramas A/B, cenários seco/médio/úmido, alavancas de flexibilização) |
| `artigo/analise/gera_figuras.py` | Gera as figuras a partir dos resultados do modelo |
| `artigo/analise/monta_docx.py` | Converte o Markdown em DOCX (pandoc + python-docx) |
| `artigo/analise/resultados_modelo.json` | Saída numérica do modelo |

## Como reproduzir

```bash
pip install matplotlib numpy python-docx
python3 artigo/analise/modelo_hidrograma.py   # roda do diretório artigo/analise (grava resultados_modelo.json)
python3 artigo/analise/gera_figuras.py
cat artigo/fonte/parte0{1..6}.md artigo/fonte/parte07.md > artigo/fonte/artigo_completo.md   # ver nota abaixo
python3 artigo/analise/monta_docx.py          # requer pandoc
```

Nota: `artigo_completo.md` coloca a seção "Anexos A e B (reservados)" depois das Referências; ao remontar, mantenha essa ordem.

## Pendências

- **Anexos A e B**: a apresentação PPTX sobre restrições hidráulicas e os dois textos sobre Belo Monte mencionados na solicitação **não foram recebidos** na sessão de elaboração. O artigo reserva uma seção de anexos para incorporá-los.
- **Verificação de fontes**: parte dos documentos oficiais foi consultada por trechos indexados (o acesso direto a alguns repositórios não estava disponível). Valores sem dupla confirmação, antigos ou divergentes estão sinalizados no texto; conferir com o texto consolidado vigente de cada ato antes de uso técnico ou jurídico.
