# Plotador Ternário Genérico

**Versão atual: `v0.3.5-alpha`**

Aplicação desktop para criação, edição e exportação de diagramas composicionais
geológicos e geoquímicos. O projeto foi concebido para reunir diferentes
diagramas científicos em uma única base, com templates selecionáveis e dados
de composição editáveis pelo usuário.

Atualmente, o software oferece um ternário geral (`A-B-C`) e o diagrama
`Wo-En-Fs` de piroxênios baseado em Morimoto (1988). A interface é construída
com Plotly e `pywebview`, usando o bundle local do Plotly para funcionar sem
CDN e sem acesso à internet.

## Principais funcionalidades atuais

### Diagramas e templates

- Template de **Ternário Geral (sem campos)**, com eixos `A`, `B` e `C`.
- Template de **Piroxênios — Morimoto (1988)**, com:
  - componentes Wollastonita (`Wo`), Enstatita (`En`) e Ferrossilita (`Fs`);
  - campos composicionais de Clinoenstatita, Clinoferrossilita, Pigeonita,
    Augita, Diopsídio e Hedenbergita;
  - linhas divisórias e nomes dos campos posicionados no diagrama.
- Troca de template sem perder os pontos já carregados na tabela.
- Dados científicos dos campos separados do código em
  [`pyroxene_fields.json`](./pyroxene_diagram/data/pyroxene_fields.json).

### Dados e tabela

- Importação de dados em:
  - `.csv`;
  - `.xls`;
  - `.xlsx`.
- Reconhecimento das colunas por nomes como `Nome`, `Nome/código`, `Sample`,
  `Wo`, `En`, `Fs`, `A`, `B` e `C`.
- Fallback para as quatro primeiras colunas válidas quando os cabeçalhos
  variarem.
- Edição dos nomes e dos valores composicionais diretamente na tabela.
- Adição manual de pontos.
- Exclusão individual e em massa.
- Checkboxes individuais e checkbox mestre para selecionar pontos.
- Sincronização bidirecional entre tabela e gráfico.

### Seleção, histórico e segurança

- Seleção de amostras por clique, Box Select e Lasso Select.
- Destaque visual das linhas selecionadas na tabela.
- Contador preciso de pontos selecionados.
- Sistema de **Desfazer/Refazer** com:
  - botões na interface;
  - `Ctrl+Z` para desfazer;
  - `Ctrl+Y` ou `Ctrl+Shift+Z` para refazer.
- Histórico para adição, edição, exclusão e importação de dados.
- Aviso ao fechar quando existem alterações ainda não exportadas.
- Fluxo de encerramento seguro para Windows/WebView2, com encerramento da
  árvore de processos e sessão privada do WebView2.

### Exportação

- Exportação do gráfico em:
  - PNG;
  - SVG;
  - TIFF.
- Exportação da tabela editada em:
  - CSV;
  - XLSX.
- Arquivos de tabela exportados podem ser reimportados imediatamente.
- Exportação do gráfico preservando a visualização atual, incluindo zoom e pan.
- Imagens exportadas com fundo branco, linhas e grid compatíveis com a
  visualização da interface.
- Bundle local do Plotly em
  [`ui/vendor/plotly.min.js`](./pyroxene_diagram/ui/vendor/plotly.min.js),
  permitindo execução offline.

## Como usar

### Instalação para desenvolvimento

O projeto requer Python 3.10 ou superior. No Windows:

```powershell
cd C:\caminho\para\diagramas_gemini_version
py -m pip install -e .
```

As dependências incluem Plotly, `pywebview`, Pillow, Kaleido, pandas,
OpenPyXL e xlrd.

### Executar

```powershell
py -m pyroxene_diagram
```

### Fluxo básico

1. Abra o aplicativo.
2. Escolha o template no seletor **Template do Diagrama**.
3. Importe uma tabela CSV ou Excel, ou utilize os pontos de exemplo.
4. Edite nomes e valores na tabela, se necessário.
5. Use clique, Box Select, Lasso Select ou os checkboxes para selecionar
   amostras.
6. Utilize os botões de exportação para salvar o gráfico ou a tabela.
7. Use **Desfazer** e **Refazer** caso precise recuperar uma alteração.

Para o template de piroxênios, a tabela deve conter uma coluna de identificação
e três colunas numéricas correspondentes a `Wo`, `En` e `Fs`. Para o ternário
geral, podem ser usadas as colunas `A`, `B` e `C`.

### Validação

Execute os testes automatizados com:

```powershell
py -m pytest
```

## Capturas de tela

As capturas de tela oficiais serão adicionadas quando a interface visual for
consolidada para a primeira versão pública. Até lá, a aplicação pode ser
executada localmente seguindo as instruções acima.

## Próximas implementações previstas

Esta seção é o roadmap público do projeto. Novos itens deverão ser adicionados
aqui conforme novas decisões de desenvolvimento forem tomadas.

### Novos templates de diagramas ternários

Planeja-se ampliar a biblioteca de templates com diagramas usados em diferentes
áreas da petrologia, geoquímica e sedimentologia.

#### Sistemas ígneos

- Diagramas de feldspatos.
- Diagramas de anfibólios.
- Diagramas QAP.
- Diagramas FAP.
- Diagramas para rochas ultramáficas.
- Diagramas de rochas vulcanoclásticas de Fisher (1966).

#### Sistemas sedimentares

- Diagrama QFR de Folk.
- Diagramas QtFl.
- Diagramas QmFl.
- Classificação de Pettijohn (1975).
- Classificação de Folk & Ward (1957).

### Legenda opcional, customizável e interativa

- Ativação ou ocultação da legenda conforme a necessidade do usuário.
- Personalização de nomes, cores e estilos dos itens da legenda.
- Criação de uma entrada na legenda ao clicar em um ponto.
- Destaque dos pontos correspondentes no gráfico ao passar o mouse sobre uma
  entrada da legenda.
- Possibilidade de organizar e controlar grupos de amostras pela legenda.

### Internacionalização

- Alternância entre português e inglês (`PT/EN`).
- Tradução dos textos da interface.
- Tradução dos títulos, rótulos, mensagens e elementos textuais dos diagramas.
- Preparação de um README em inglês, possivelmente em
  [`README-en.md`](./README-en.md), mantido em paralelo com esta documentação.

### Grid e eixos mais customizáveis

- Controle da densidade do grid.
- Mostrar ou ocultar valores dos eixos.
- Configuração da fonte dos valores e rótulos.
- Remoção seletiva de valores individuais.
- Mostrar ou ocultar o tracinho de referência associado aos valores.
- Maior controle visual dos eixos conforme o tipo de diagrama.

### Linhas e áreas desenháveis

- Desenho manual de linhas de tendência.
- Criação de áreas e campos auxiliares diretamente no diagrama.
- Uso de linhas para comparação com tendências publicadas na literatura.
- Sobreposição de limites, referências e interpretações do usuário.
- Possibilidade futura de salvar esses elementos junto da exportação da figura.

### Personalização visual avançada

- Definição de cores dos pontos e elementos do diagrama.
- Controle de transparência.
- Ajuste de espessuras de linhas e contornos.
- Ajuste do tamanho e da forma dos marcadores.
- Estilos independentes para grupos, campos, referências e amostras.
- Presets visuais para publicação, apresentação e exploração de dados.

### Diagramas não ternários

Depois da consolidação do sistema de templates ternários, a arquitetura deverá
ser ampliada para diagramas de outros formatos, incluindo:

- TAS.
- Elementos-traço e terras-raras normalizados.
- Piper.
- Harker.
- Diagramas de discriminação tectônica.
- Outros diagramas composicionais definidos pela comunidade.

## Arquitetura e documentação científica

Os templates são atualmente híbridos: a estrutura dos templates é registrada
em Python, enquanto os dados geométricos dos campos de Morimoto ficam em JSON.
A lógica de conversão, importação, construção dos traces, ponte Python–JavaScript
e interface está separada em módulos para facilitar a adição de novos
diagramas.

Os limites científicos fixos do template de piroxênios estão em
[`pyroxene_fields.json`](./pyroxene_diagram/data/pyroxene_fields.json) e não
são editáveis pela interface.

## Estado do projeto

O software está em fase **alpha**. A base atual já permite testar o fluxo
completo de seleção, edição, histórico, importação e exportação, mas a API de
templates, a internacionalização, a personalização avançada e o empacotamento
portátil ainda estão em evolução.

Contribuições, sugestões de novos diagramas e discussões sobre fontes
científicas serão bem-vindas quando o repositório público for disponibilizado.
