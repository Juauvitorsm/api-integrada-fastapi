from pydantic import BaseModel
from typing import Optional
from datetime import date

class EmpresasBase(BaseModel):
    nome_empresa: str
    diretor_empresa: str

class Empresas(EmpresasBase):
    id_empresa: int

    class Config:
        from_attributes = True

class FaturamentoBase(BaseModel):
    id_empresa: int
    faturamento_mensal: float
    faturamento_anual: float

class FaturamentoCreate(FaturamentoBase):
    id_faturamento: int

class Faturamento(FaturamentoBase):
    id_faturamento: int
    class Config:
        from_attributes = True

class ProdutosVendidosBase(BaseModel):
    id_faturamento: int
    nome_produto: str
    produtos_vendidos: int

class ProdutosVendidosCreate(ProdutosVendidosBase):
    id_venda: int

class ProdutosVendidos(ProdutosVendidosBase):
    id_venda: int
    class Config:
        from_attributes = True


class DetalhesProdutosBase(BaseModel):
    id_empresa: int
    nome_produto: str
    categoria: str
    preco_unitario: float
    margem_lucro_percentual: float
    data_lancamento: date

class DetalhesProdutosUpdate(BaseModel):
    id_empresa: int | None = None
    nome_produto: str | None = None
    categoria: str | None = None
    preco_unitario: float | None = None
    margem_lucro_percentual: float | None = None
    data_lancamento: date | None = None

class DetalhesProdutosCreate(DetalhesProdutosBase):
    pass
    
class DetalhesProdutos(DetalhesProdutosBase):
    id_produto: int
    class Config:
        from_attributes = True


class AvaliacoesDiretorEmpresaBase(BaseModel):
    id_empresa: int
    nota_diretor: int
    nota_geral_empresa: int
    comentario: str

class AvaliacoesDiretorEmpresaUpdate(BaseModel):
    nota_diretor: int | None = None
    nota_geral_empresa: int | None = None
    comentario: str | None = None

class AvaliacoesDiretorEmpresaCreate(AvaliacoesDiretorEmpresaBase):
    pass

class AvaliacoesDiretorEmpresa(AvaliacoesDiretorEmpresaBase):
    id_avaliacao: int
    class Config:
        from_attributes = True