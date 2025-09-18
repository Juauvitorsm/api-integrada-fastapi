from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from database import Base

class Empresas(Base):
    __tablename__ = "empresas"
    __table_args__ = {'schema': 'public'}

    id_empresa = Column(Integer, primary_key=True, autoincrement=True)
    nome_empresa = Column(String)
    diretor_empresa = Column(String)

    faturamentos = relationship("Faturamento", back_populates="empresa")
    detalhes_produtos = relationship("DetalhesProdutos", back_populates="empresa")
    avaliacoes = relationship("AvaliacoesDiretorEmpresa", back_populates="empresa")

class Faturamento(Base):
    __tablename__ = "faturamento"
    __table_args__ = {'schema': 'public'}

    id_faturamento = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey('public.empresas.id_empresa'))
    faturamento_mensal = Column(Float)
    faturamento_anual = Column(Float)

    empresa = relationship("Empresas", back_populates="faturamentos")
    produtos_vendidos = relationship("ProdutosVendidos", back_populates="faturamento")

class ProdutosVendidos(Base):
    __tablename__ = "produtos_vendidos"
    __table_args__ = {'schema': 'public'}

    id_venda = Column(Integer, primary_key=True)
    id_faturamento = Column(Integer, ForeignKey('public.faturamento.id_faturamento'))
    nome_produto = Column(String)
    produtos_vendidos = Column(Integer)

    faturamento = relationship("Faturamento", back_populates="produtos_vendidos")

class DetalhesProdutos(Base):
    __tablename__ = "detalhes_produtos"
    __table_args__ = {'schema': 'public'}

    id_produto = Column(Integer, primary_key=True, autoincrement=True)
    id_empresa = Column(Integer, ForeignKey('public.empresas.id_empresa'))
    nome_produto = Column(String)
    categoria = Column(String)
    preco_unitario = Column(Float)
    margem_lucro_percentual = Column(Float)
    data_lancamento = Column(Date)

    empresa = relationship("Empresas", back_populates="detalhes_produtos")

class AvaliacoesDiretorEmpresa(Base):
    __tablename__ = "avaliacoes_diretor_empresa"
    __table_args__ = {'schema': 'public'}

    id_avaliacao = Column(Integer, primary_key=True, autoincrement=True)
    id_empresa = Column(Integer, ForeignKey('public.empresas.id_empresa'))
    nota_diretor = Column(Integer)
    nota_geral_empresa = Column(Integer)
    comentario = Column(String)

    empresa = relationship("Empresas", back_populates="avaliacoes")