
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

ARQUIVO_DADOS = "precos_supermercado.json"


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

    def carregar_dados(self):
        if os.path.exists(ARQUIVO_DADOS):
            try:
                with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
                    dados = json.load(arquivo)
                    return dados if isinstance(dados, list) else []
            except (json.JSONDecodeError, OSError):
                messagebox.showwarning(
                    "Aviso",
                    "Não foi possível ler o arquivo de preços."
                )
        return []

    def salvar_dados(self):
        try:
            with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
                json.dump(
                    self.dados,
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )
        except OSError as erro:
            messagebox.showerror(
                "Erro ao salvar",
                str(erro)
            )

    def configurar_estilo(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Treeview",
            rowheight=30,
            font=("Arial", 10)
        )
        estilo.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold")
        )

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

        ttk.Label(formulario, text="Produto:").grid(
            row=0, column=0, sticky="w", padx=5
        )
        self.entrada_produto = ttk.Entry(formulario, width=25)
        self.entrada_produto.grid(
            row=1, column=0, padx=5, pady=5, sticky="ew"
        )

        ttk.Label(formulario, text="Supermercado:").grid(
            row=0, column=1, sticky="w", padx=5
        )
        self.entrada_mercado = ttk.Entry(formulario, width=25)
        self.entrada_mercado.grid(
            row=1, column=1, padx=5, pady=5, sticky="ew"
        )

        ttk.Label(formulario, text="Preço (R$):").grid(
            row=0, column=2, sticky="w", padx=5
        )
        self.entrada_preco = ttk.Entry(formulario, width=15)
        self.entrada_preco.grid(
            row=1, column=2, padx=5, pady=5, sticky="ew"
        )

        ttk.Button(
            formulario,
            text="Adicionar preço",
            command=self.adicionar_preco
        ).grid(row=1, column=3, padx=8)

        for coluna in range(3):
            formulario.columnconfigure(coluna, weight=1)

        filtros = ttk.Frame(self.root, padding=(15, 0))
        filtros.pack(fill="x", pady=5)

        ttk.Label(
            filtros,
            text="Filtrar produto:"
        ).pack(side="left", padx=(0, 8))

        self.filtro = ttk.Combobox(
            filtros,
            state="readonly",
            width=30
        )
        self.filtro.pack(side="left")
        self.filtro.bind(
            "<<ComboboxSelected>>",
            lambda evento: self.atualizar_tabela()
        )

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

        barra = ttk.Scrollbar(
            area_tabela,
            orient="vertical",
            command=self.tabela.yview
        )
        self.tabela.configure(yscrollcommand=barra.set)

        self.tabela.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        rodape = ttk.Frame(self.root, padding=(15, 0, 15, 12))
        rodape.pack(fill="x")

        self.resultado = ttk.Label(
            rodape,
            text="Cadastre produtos para começar.",
            font=("Arial", 11, "bold")
        )
        self.resultado.pack(side="left", fill="x", expand=True)

        ttk.Button(
            rodape,
            text="Excluir selecionado",
            command=self.excluir_preco
        ).pack(side="right")

    def converter_preco(self, texto):
        texto = texto.strip().replace("R$", "").replace(" ", "")

        if "," in texto:
            texto = texto.replace(".", "").replace(",", ".")

        preco = float(texto)

        if preco < 0:
            raise ValueError("O preço não pode ser negativo.")

        return round(preco, 2)

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
            preco = self.converter_preco(
                self.entrada_preco.get()
            )
        except ValueError:
            messagebox.showerror(
                "Preço inválido",
                "Digite um preço válido, por exemplo: 12,90."
            )
            return

        self.dados.append({
            "produto": produto,
            "mercado": mercado,
            "preco": preco
        })

        self.salvar_dados()
        self.atualizar_tabela()

        self.entrada_produto.delete(0, tk.END)
        self.entrada_mercado.delete(0, tk.END)
        self.entrada_preco.delete(0, tk.END)
        self.entrada_produto.focus()

        self.resultado.config(text="Preço cadastrado com sucesso.")

    def atualizar_tabela(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        selecionado = self.filtro.get()

        produtos = sorted({
            item["produto"] for item in self.dados
        }, key=str.casefold)

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

        registros = sorted(
            registros,
            key=lambda item: (
                item["produto"].casefold(),
                item["preco"]
            )
        )

        for indice, item in enumerate(registros):
            self.tabela.insert(
                "",
                "end",
                iid=str(indice),
                values=(
                    item["produto"],
                    item["mercado"],
                    f"R$ {item['preco']:.2f}".replace(".", ",")
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

        registros = [
            item for item in self.dados
            if item["produto"] == produto
        ]

        if not registros:
            messagebox.showinfo(
                "Comparação",
                "Não há preços cadastrados para esse produto."
            )
            return

        menor = min(registros, key=lambda item: item["preco"])
        maior = max(registros, key=lambda item: item["preco"])
        diferenca = maior["preco"] - menor["preco"]

        self.resultado.config(
            text=(
                f"Mais barato: {menor['mercado']} "
                f"(R$ {menor['preco']:.2f})"
            ).replace(".", ",")
        )

        mensagem = (
            f"Produto: {produto}\n\n"
            f"Menor preço: {menor['mercado']} — "
            f"R$ {menor['preco']:.2f}\n"
            f"Maior preço: {maior['mercado']} — "
            f"R$ {maior['preco']:.2f}\n\n"
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

        produto = self.filtro.get()
        registros = self.dados

        if produto and produto != "Todos":
            registros = [
                item for item in self.dados
                if item["produto"] == produto
            ]

        indice = int(selecao[0])

        if indice >= len(registros):
            return

        registro = registros[indice]

        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Excluir o preço de {registro['produto']} "
            f"no {registro['mercado']}?"
        ):
            return

        self.dados.remove(registro)
        self.salvar_dados()
        self.atualizar_tabela()
        self.resultado.config(text="Registro excluído.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ComparadorApp(root)
    root.mainloop()
