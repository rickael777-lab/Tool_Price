import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

ARQUIVO_DADOS = "produtos_supermercados.csv"
COLUNAS = ["Produto", "Preco_Vitoria", "Preco_Rosario", "Preco_Pekeno"]

MERCADOS = {
    "Vitória": "Preco_Vitoria",
    "Rosário": "Preco_Rosario",
    "Pekeno": "Preco_Pekeno",
}


class ComparadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Preços de Supermercado")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)

        self.dados = self.carregar_dados()

        self.configurar_estilo()
        self.criar_interface()
        self.atualizar_tabela()

    def converter_preco(self, texto):
        texto = str(texto).strip().replace("R$", "").replace(" ", "")
        if not texto:
            return None

        if "," in texto:
            texto = texto.replace(".", "").replace(",", ".")

        preco = float(texto)
        if preco < 0:
            raise ValueError("O preço não pode ser negativo.")
        return round(preco, 2)

    def carregar_dados(self):
        if not os.path.exists(ARQUIVO_DADOS):
            messagebox.showwarning(
                "Arquivo não encontrado",
                f"Não encontrei '{ARQUIVO_DADOS}'. "
                "Coloque o CSV na mesma pasta deste programa."
            )
            return []

        dados = []
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8-sig", newline="") as arquivo:
                leitor = csv.DictReader(arquivo, delimiter=";")

                if not leitor.fieldnames:
                    return []

                campos = {campo.strip().casefold(): campo for campo in leitor.fieldnames}
                obrigatorios = ["produto", "preco_vitoria", "preco_rosario", "preco_pekeno"]

                if not all(campo in campos for campo in obrigatorios):
                    messagebox.showerror(
                        "CSV inválido",
                        "O arquivo precisa ter estas colunas:\n"
                        "Produto;Preco_Vitoria;Preco_Rosario;Preco_Pekeno"
                    )
                    return []

                for linha in leitor:
                    produto = (linha.get(campos["produto"]) or "").strip()
                    if not produto:
                        continue

                    registro = {"produto": produto}
                    for coluna in obrigatorios[1:]:
                        valor = linha.get(campos[coluna], "")
                        registro[coluna] = self.converter_preco(valor) if str(valor or "").strip() else None
                    dados.append(registro)

        except (OSError, csv.Error, ValueError) as erro:
            messagebox.showerror(
                "Erro ao carregar CSV",
                f"Não foi possível ler os preços:\n{erro}"
            )

        return dados

    def salvar_dados(self):
        try:
            with open(ARQUIVO_DADOS, "w", encoding="utf-8-sig", newline="") as arquivo:
                escritor = csv.DictWriter(
                    arquivo,
                    fieldnames=COLUNAS,
                    delimiter=";"
                )
                escritor.writeheader()

                for item in sorted(self.dados, key=lambda x: x["produto"].casefold()):
                    linha = {"Produto": item["produto"]}
                    for coluna in COLUNAS[1:]:
                        preco = item.get(coluna.casefold())
                        linha[coluna] = (
                            f"{preco:.2f}".replace(".", ",")
                            if preco is not None else ""
                        )
                    escritor.writerow(linha)

        except OSError as erro:
            messagebox.showerror("Erro ao salvar", str(erro))

    def configurar_estilo(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=30, font=("Arial", 10))
        estilo.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    def criar_interface(self):
        titulo = tk.Label(
            self.root,
            text="Comparador de Preços",
            font=("Arial", 22, "bold"),
            bg="#17324d",
            fg="white",
            pady=18
        )
        titulo.pack(fill="x")

        formulario = ttk.LabelFrame(
            self.root,
            text="Cadastrar produto e preço",
            padding=12
        )
        formulario.pack(fill="x", padx=15, pady=12)

        ttk.Label(formulario, text="Produto:").grid(row=0, column=0, sticky="w", padx=5)
        self.entrada_produto = ttk.Entry(formulario, width=25)
        self.entrada_produto.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        ttk.Label(formulario, text="Supermercado:").grid(row=0, column=1, sticky="w", padx=5)
        self.entrada_mercado = ttk.Combobox(
            formulario,
            values=list(MERCADOS.keys()),
            state="readonly",
            width=22
        )
        self.entrada_mercado.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.entrada_mercado.set("Vitória")

        ttk.Label(formulario, text="Preço (R$):").grid(row=0, column=2, sticky="w", padx=5)
        self.entrada_preco = ttk.Entry(formulario, width=15)
        self.entrada_preco.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        ttk.Button(
            formulario,
            text="Adicionar preço",
            command=self.adicionar_preco
        ).grid(row=1, column=3, padx=8)

        for coluna in range(3):
            formulario.columnconfigure(coluna, weight=1)

        filtros = ttk.Frame(self.root, padding=(15, 0))
        filtros.pack(fill="x", pady=5)

        ttk.Label(filtros, text="Filtrar produto:").pack(side="left", padx=(0, 8))

        self.filtro = ttk.Combobox(filtros, state="readonly", width=30)
        self.filtro.pack(side="left")
        self.filtro.bind("<<ComboboxSelected>>", lambda evento: self.atualizar_tabela())

        ttk.Button(
            filtros,
            text="Comparar preços",
            command=self.comparar_precos
        ).pack(side="left", padx=10)

        ttk.Button(
            filtros,
            text="Mostrar todos",
            command=self.mostrar_todos
        ).pack(side="left")

        area_tabela = ttk.Frame(self.root, padding=15)
        area_tabela.pack(fill="both", expand=True)

        colunas = ("produto", "mercado", "preco")
        self.tabela = ttk.Treeview(
            area_tabela,
            columns=colunas,
            show="headings",
            selectmode="browse"
        )

        self.tabela.heading("produto", text="Produto")
        self.tabela.heading("mercado", text="Supermercado")
        self.tabela.heading("preco", text="Preço")

        self.tabela.column("produto", width=300)
        self.tabela.column("mercado", width=300)
        self.tabela.column("preco", width=150, anchor="e")

        barra = ttk.Scrollbar(area_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        rodape = ttk.Frame(self.root, padding=(15, 0, 15, 12))
        rodape.pack(fill="x")

        self.resultado = ttk.Label(
            rodape,
            text="Produtos carregados do arquivo CSV.",
            font=("Arial", 11, "bold")
        )
        self.resultado.pack(side="left", fill="x", expand=True)

        ttk.Button(
            rodape,
            text="Excluir selecionado",
            command=self.excluir_preco
        ).pack(side="right")

    def adicionar_preco(self):
        produto = self.entrada_produto.get().strip()
        mercado = self.entrada_mercado.get().strip()

        if not produto or not mercado:
            messagebox.showwarning(
                "Campos obrigatórios",
                "Informe o produto e o supermercado."
            )
            return

        try:
            preco = self.converter_preco(self.entrada_preco.get())
            if preco is None:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Preço inválido",
                "Digite um preço válido, por exemplo: 12,90."
            )
            return

        coluna = MERCADOS[mercado]
        registro = next(
            (item for item in self.dados
             if item["produto"].casefold() == produto.casefold()),
            None
        )

        if registro is None:
            registro = {
                "produto": produto,
                "preco_vitoria": None,
                "preco_rosario": None,
                "preco_pekeno": None
            }
            self.dados.append(registro)

        registro[coluna.casefold()] = preco

        self.salvar_dados()
        self.atualizar_tabela()

        self.entrada_produto.delete(0, tk.END)
        self.entrada_preco.delete(0, tk.END)
        self.entrada_produto.focus()
        self.resultado.config(text="Preço cadastrado/atualizado com sucesso.")

    def atualizar_tabela(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        selecionado = self.filtro.get()
        produtos = sorted(
            {item["produto"] for item in self.dados},
            key=str.casefold
        )

        self.filtro["values"] = ["Todos"] + produtos
        if selecionado not in self.filtro["values"]:
            selecionado = "Todos"
        self.filtro.set(selecionado or "Todos")

        registros = self.dados
        if selecionado and selecionado != "Todos":
            registros = [
                item for item in self.dados
                if item["produto"] == selecionado
            ]

        for registro in sorted(registros, key=lambda x: x["produto"].casefold()):
            for nome_mercado, coluna in MERCADOS.items():
                preco = registro.get(coluna.casefold())
                if preco is not None:
                    self.tabela.insert(
                        "",
                        "end",
                        values=(
                            registro["produto"],
                            nome_mercado,
                            f"R$ {preco:.2f}".replace(".", ",")
                        )
                    )

    def comparar_precos(self):
        produto = self.filtro.get()

        if not produto or produto == "Todos":
            messagebox.showinfo(
                "Comparação",
                "Selecione um produto específico no filtro."
            )
            return

        registro = next(
            (item for item in self.dados if item["produto"] == produto),
            None
        )

        if not registro:
            messagebox.showinfo("Comparação", "Produto não encontrado.")
            return

        precos = [
            (mercado, registro[coluna.casefold()])
            for mercado, coluna in MERCADOS.items()
            if registro.get(coluna.casefold()) is not None
        ]

        if not precos:
            messagebox.showinfo(
                "Comparação",
                "Não há preços cadastrados para esse produto."
            )
            return

        menor = min(precos, key=lambda x: x[1])
        maior = max(precos, key=lambda x: x[1])
        diferenca = maior[1] - menor[1]

        self.resultado.config(
            text=f"Mais barato: {menor[0]} (R$ {menor[1]:.2f})".replace(".", ",")
        )

        mensagem = (
            f"Produto: {produto}\n\n"
            f"Menor preço: {menor[0]} — R$ {menor[1]:.2f}\n"
            f"Maior preço: {maior[0]} — R$ {maior[1]:.2f}\n\n"
            f"Diferença: R$ {diferenca:.2f}"
        ).replace(".", ",")

        messagebox.showinfo("Resultado da comparação", mensagem)

    def mostrar_todos(self):
        self.filtro.set("Todos")
        self.atualizar_tabela()
        self.resultado.config(text="Exibindo todos os preços.")

    def excluir_preco(self):
        selecao = self.tabela.selection()

        if not selecao:
            messagebox.showwarning(
                "Seleção necessária",
                "Selecione um preço na tabela."
            )
            return

        produto, mercado, preco_texto = self.tabela.item(selecao[0], "values")
        coluna = MERCADOS[mercado]

        registro = next(
            (item for item in self.dados if item["produto"] == produto),
            None
        )
        if registro is None:
            return

        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Excluir o preço de {produto} no supermercado {mercado}?"
        ):
            return

        registro[coluna.casefold()] = None

        if all(registro.get(c.casefold()) is None for c in COLUNAS[1:]):
            self.dados.remove(registro)

        self.salvar_dados()
        self.atualizar_tabela()
        self.resultado.config(text="Registro excluído.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ComparadorApp(root)
    root.mainloop()
