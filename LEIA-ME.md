# Bunyy Wiki

Wiki de fãs da HQ e novel **BUNYY**, de Toom. Site não oficial.

---

## Parte 1 — Colocar o site no ar (só uma vez)

Faça esta parte num computador. Pelo celular dá para editar depois, mas subir os arquivos pela primeira vez é bem mais fácil no PC.

1. **Crie o repositório.** No GitHub, clique em **New repository**. Dê um nome, por exemplo `bunyy-wiki`, deixe como **Public** e clique em **Create repository**.
2. **Suba os arquivos.** Descompacte o zip no computador. Na página do repositório, clique em **uploading an existing file** e arraste o *conteúdo* da pasta (não a pasta em si). O GitHub aceita no máximo 100 arquivos por vez, então faça em duas levas:
   - primeiro, tudo **menos** a pasta `imagens`;
   - depois, a pasta `imagens`.

   Em cada leva, clique em **Commit changes** no fim da página.
3. **Confira os arquivos ocultos.** Na lista do repositório precisam aparecer a pasta `.github` e o arquivo `.pages.yml`. No Mac, a pasta `.github` some no Finder: aperte `Cmd + Shift + .` para mostrar arquivos ocultos antes de arrastar.
4. **Ligue o GitHub Pages.** Vá em **Settings → Pages**. Em **Source**, escolha **GitHub Actions**.
5. **Espere a primeira publicação.** Abra a aba **Actions**. Quando "Publicar site" ficar com um ✓ verde (1 a 2 minutos), o site estará em `https://SEU-USUARIO.github.io/bunyy-wiki/`. Se ainda não tiver rodado, clique em "Publicar site" e depois em **Run workflow**.

## Parte 2 — Conectar o painel visual (só uma vez)

1. Entre em **https://app.pagescms.org** e clique para entrar com a sua conta do GitHub.
2. Quando pedir, **instale o app do Pages CMS** na sua conta e dê acesso ao repositório `bunyy-wiki`.
3. Abra o repositório no painel. Ele lê o arquivo `.pages.yml` e mostra, na lateral:
   - **Páginas da wiki**: todos os personagens, lugares, capítulos e conceitos;
   - **Página inicial**: título, novidades, spoiler e "Você sabia…";
   - **Capítulos (HQ e novel)**: capas, títulos e links das novels;
   - **Mapa da jornada**: as paradas do mapa.

## Parte 3 — Editar no dia a dia

1. Abra o painel, escolha o que quer mudar, edite e clique em **Save**.
2. Em mais ou menos 1 minuto o site atualiza sozinho. Recarregue a página para ver.

O painel funciona pelo celular também.

### Atalhos dentro dos textos

| Escreva | Vira |
|---|---|
| `{cap 3}` | etiqueta do capítulo 3 da novel |
| `{hq 3}` | etiqueta do capítulo 3 da HQ (abre na Fliptru) |
| `[Any](#any)` | link para a página da Any |

O que vem depois do `#` é o nome do arquivo da página sem o `.md` (`bunyy-grimm`, `capitulo-10`, `dominio-sombrio`...). Link para uma página que não existe vira texto normal, sem quebrar nada.

### Coisas comuns

- **Página nova:** em "Páginas da wiki", clique em **Add an entry**. Escolha a aba onde ela aparece (Personagens, Lugares...) e, se for personagem, o lado.
- **Imagem:** use os campos de imagem (principal, galeria, outras versões). O painel salva a foto na pasta `imagens/`.
- **Imagem do cartão:** é a foto que aparece atrás do nome nas listas das abas (Personagens, Bestas e criaturas...). Prefira uma imagem deitada. Se ficar vazio, o site usa a primeira de "Outras versões" ou a imagem principal.
- **Criatura nova:** crie a página com a aba **Criaturas** e escolha o tipo: **Com nome** (Caronte, Dentuço...) ou **Espécie** (dragões, sereias...).
- **Nova fala do Toom:** abra a página do personagem e adicione um item em "Segundo o Toom". Preencha a data no formato `2026-10-24` e cole o link da mensagem do Discord.
- **Novo capítulo:** em "Capítulos", adicione a HQ e/ou a novel. Depois crie a página `capitulo-11` com o resumo.
- **Novidade na página inicial:** em "Página inicial → Novidades", adicione no topo da lista.

### Deu errado?

- Se o site não atualizou, olhe a aba **Actions** do GitHub. Um ✗ vermelho mostra o erro; quase sempre é um campo preenchido de um jeito estranho.
- Tudo fica guardado no histórico do GitHub: dá para abrir qualquer arquivo, clicar em **History** e voltar para a versão anterior.

### Mais gente editando

Em **Settings → Collaborators**, adicione o usuário do GitHub da pessoa. Ela entra no mesmo painel (app.pagescms.org) com a conta dela.

---

## Como o site é montado (para curiosos)

- `conteudo/paginas/*.md`: uma página por arquivo, com os dados no topo (entre `---`) e o texto em Markdown embaixo.
- `conteudo/inicio.yml`, `capitulos.yml`, `mapa.yml`: dados da página inicial, dos capítulos e do mapa.
- `imagens/`: todas as imagens.
- `ferramentas/construir.py`: junta tudo num único `index.html`. O GitHub roda esse programa a cada mudança (`.github/workflows/publicar.yml`).
- `ferramentas/modelo.html`: o visual do site (cores, abas, mapa).
