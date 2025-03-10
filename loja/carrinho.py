class Carrinho:
    def __init__(self, request):
        self.session = request.session
        carrinho = self.session.get('carrinho')
        if not carrinho:
            carrinho = self.session['carrinho'] = {}
        self.carrinho = carrinho

    def adicionar(self, produto_id, quantidade=1):
        produto_id = str(produto_id)
        if produto_id in self.carrinho:
            self.carrinho[produto_id]['quantidade'] += quantidade
        else:
            self.carrinho[produto_id] = {'quantidade': quantidade}
        self.salvar()

    def remover(self, produto_id):
        produto_id = str(produto_id)
        if produto_id in self.carrinho:
            del self.carrinho[produto_id]
            self.salvar()

    def salvar(self):
        self.session.modified = True

    def limpar(self):
        self.session['carrinho'] = {}
        self.salvar()

    def listar_itens(self):
        return self.carrinho
