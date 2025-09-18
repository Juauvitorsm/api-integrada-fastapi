from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func, text
from typing import List, Dict
from app.api import models as api_models
from app.api import schemas as api_schemas
from app.auth.endpoints import get_current_user
from app.auth.models import User
from database import get_db 

router = APIRouter()

@router.get("/empresas/")
def read_empresas(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(api_models.Empresas)
    empresas = db.execute(stmt).scalars().all()
    return empresas

@router.get("/faturamento/")
def read_faturamento(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(api_models.Faturamento)
    faturamento = db.execute(stmt).scalars().all()
    return faturamento

@router.get("/produtos/")
def read_produtos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(api_models.ProdutosVendidos)
    produtos = db.execute(stmt).scalars().all()
    return produtos

@router.get("/detalhes_produtos/")
def read_detalhes_produtos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(api_models.DetalhesProdutos)
    detalhes_produtos = db.execute(stmt).scalars().all()
    return detalhes_produtos

@router.get("/avaliacoes/")
def read_avaliacoes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(api_models.AvaliacoesDiretorEmpresa)
    avaliacoes = db.execute(stmt).scalars().all()
    return avaliacoes

@router.post("/empresas/", response_model=api_schemas.Empresas)
def create_empresa(empresa: api_schemas.EmpresasBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not empresa.nome_empresa.strip() or not empresa.diretor_empresa.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Campos não podem ser vazios.")
    
    db_empresa = api_models.Empresas(**empresa.model_dump())
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    return db_empresa

@router.post("/detalhes_produtos/", response_model=api_schemas.DetalhesProdutos)
def create_detalhes_produtos(detalhes_produtos: api_schemas.DetalhesProdutosCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_detalhes_produtos = api_models.DetalhesProdutos(**detalhes_produtos.model_dump())
    db.add(db_detalhes_produtos)
    db.commit()
    db.refresh(db_detalhes_produtos)
    return db_detalhes_produtos

@router.post("/avaliacoes/", response_model=api_schemas.AvaliacoesDiretorEmpresa)
def create_avaliacao(avaliacao: api_schemas.AvaliacoesDiretorEmpresaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    empresa_existe = db.query(api_models.Empresas).filter(api_models.Empresas.id_empresa == avaliacao.id_empresa).first()
    if not empresa_existe:
        raise HTTPException(status_code=404, detail=f"Empresa com ID {avaliacao.id_empresa} não encontrada.")

    db_avaliacao = api_models.AvaliacoesDiretorEmpresa(**avaliacao.model_dump())
    db.add(db_avaliacao)
    db.commit()
    db.refresh(db_avaliacao)
    return db_avaliacao

@router.put("/empresas/{id_empresa}", response_model=api_schemas.EmpresasBase)
def update_empresa(id_empresa: int, empresa_data: api_schemas.EmpresasBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = update(api_models.Empresas).where(api_models.Empresas.id_empresa == id_empresa).values(empresa_data.model_dump())
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    db.commit()
    db_empresa = db.query(api_models.Empresas).filter(api_models.Empresas.id_empresa == id_empresa).first()
    return db_empresa

@router.put("/detalhes_produtos/{id_produto}")
def update_detalhes_produtos(id_produto: int, produto_data: api_schemas.DetalhesProdutosUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_produto = db.query(api_models.DetalhesProdutos).filter(api_models.DetalhesProdutos.id_produto == id_produto).first()
    if not db_produto:
        raise HTTPException(status_code=404, detail="Detalhes do produto não encontrados.")
    
    update_data = produto_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_produto, key, value)
        
    db.commit()
    db.refresh(db_produto)
    return db_produto

@router.put("/avaliacoes/{id_avaliacao}")
def update_avaliacoes(id_avaliacao: int, avaliacao_data: api_schemas.AvaliacoesDiretorEmpresaUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    db_avaliacao = db.query(api_models.AvaliacoesDiretorEmpresa).filter(api_models.AvaliacoesDiretorEmpresa.id_avaliacao == id_avaliacao).first()
    if not db_avaliacao:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")
    
    update_data = avaliacao_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_avaliacao, key, value)
        
    db.commit()
    db.refresh(db_avaliacao)
    return db_avaliacao


@router.get("/pioresdiretores/")
def get_piores(db:Session= Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt= select(api_models.Empresas.diretor_empresa, api_models.Faturamento.faturamento_anual).join(api_models.Faturamento, api_models.Empresas.id_empresa== api_models.Faturamento.id_empresa).order_by(api_models.Faturamento.faturamento_anual.asc()).limit(4)
    piores = db.execute(stmt).all()
    
    piores_list = []
    for diretor, faturamento in piores:
        piores_list.append({"diretor_empresa": diretor, "faturamento_anual": faturamento})
    return piores_list

@router.get("/faturamento_por_produto")
def get_empresa_produtos(db:Session=Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(api_models.ProdutosVendidos.nome_produto, api_models.Empresas.nome_empresa).join(api_models.Faturamento,api_models.ProdutosVendidos.id_faturamento== api_models.Faturamento.id_faturamento).join(api_models.Empresas, api_models.Empresas.id_empresa==api_models.Faturamento.id_empresa).order_by(api_models.ProdutosVendidos.produtos_vendidos.asc())
    vendas= db.execute(stmt).all()
    vendas_lista = []
    for produto, empresa in vendas:
       vendas_lista.append({"nome_produto": produto,"nome_empresa": empresa})
    return vendas_lista

@router.get("/insights/")
def get_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = (
        select(
            api_models.Empresas.nome_empresa,
            func.sum(api_models.Faturamento.faturamento_anual).label("faturamento_total_anual"),
            func.avg(api_models.AvaliacoesDiretorEmpresa.nota_geral_empresa).label("media_nota_empresa")
        )
        .join(api_models.Faturamento)
        .join(api_models.AvaliacoesDiretorEmpresa)
        .group_by(api_models.Empresas.nome_empresa)
    )
    
    insights = db.execute(stmt).all()
    insights_list = []
    for insight in insights:
        insights_list.append(insight._asdict())
    return insights_list

@router.get("/insights/maior_lucro/")
def get_maior_lucro(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = (
        select(
            api_models.Empresas.diretor_empresa,
            api_models.DetalhesProdutos.nome_produto,
            api_models.Empresas.nome_empresa,
            func.sum(api_models.Faturamento.faturamento_anual).label('faturamento_total'),
            func.sum(api_models.ProdutosVendidos.produtos_vendidos).label('total_produtos_vendidos')
        )
        .join(api_models.Faturamento, api_models.Empresas.id_empresa == api_models.Faturamento.id_empresa)
        .join(api_models.ProdutosVendidos, api_models.Faturamento.id_faturamento == api_models.ProdutosVendidos.id_faturamento)
        .join(api_models.DetalhesProdutos, api_models.Empresas.id_empresa == api_models.DetalhesProdutos.id_empresa)
        .group_by(api_models.Empresas.diretor_empresa, api_models.Empresas.nome_empresa, api_models.DetalhesProdutos.nome_produto)
        .order_by(text('faturamento_total desc'))
    )
    
    results = db.execute(query).all()
    melhores = []
    for row in results:
        melhores.append(row._asdict())

    return melhores

@router.get("/melhoresdiretores/")
def get_piores(db:Session= Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt= select(api_models.Empresas.diretor_empresa, api_models.Faturamento.faturamento_anual).join(api_models.Faturamento, api_models.Empresas.id_empresa== api_models.Faturamento.id_empresa).limit(4)
    melhores = db.execute(stmt).all()
    
    melhores_list = []
    for diretor, faturamento in melhores:
        melhores_list.append({"diretor_empresa": diretor, "faturamento_anual": faturamento})
    return melhores_list


@router.post("/faturamento/", response_model=api_schemas.Faturamento)
def create_faturamento(faturamento: api_schemas.FaturamentoBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    empresa_existe = db.query(api_models.Empresas).filter(api_models.Empresas.id_empresa == faturamento.id_empresa).first()
    if not empresa_existe:
        raise HTTPException(status_code=404, detail=f"Empresa com ID {faturamento.id_empresa} não encontrada.")
    
    db_faturamento = api_models.Faturamento(**faturamento.model_dump())
    db.add(db_faturamento)
    db.commit()
    db.refresh(db_faturamento)
    return db_faturamento

@router.post("/produtos_vendidos/", response_model=api_schemas.ProdutosVendidos)
def create_produtos_vendidos(produto_vendido: api_schemas.ProdutosVendidosBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    faturamento_existe = db.query(api_models.Faturamento).filter(api_models.Faturamento.id_faturamento == produto_vendido.id_faturamento).first()
    if not faturamento_existe:
        raise HTTPException(status_code=404, detail=f"Faturamento com ID {produto_vendido.id_faturamento} não encontrado.")

    db_produto = api_models.ProdutosVendidos(**produto_vendido.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto


@router.put("/faturamento/{id_faturamento}", response_model=api_schemas.FaturamentoBase)
def update_faturamento(id_faturamento: int, faturamento_data: api_schemas.FaturamentoUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_faturamento = db.query(api_models.Faturamento).filter(api_models.Faturamento.id_faturamento == id_faturamento).first()
    if not db_faturamento:
        raise HTTPException(status_code=404, detail="Faturamento não encontrado.")
    
    update_data = faturamento_data.model_dump(exclude_unset=True)
    if "id_empresa" in update_data:
        empresa_existe = db.query(api_models.Empresas).filter(api_models.Empresas.id_empresa == update_data["id_empresa"]).first()
        if not empresa_existe:
            raise HTTPException(status_code=404, detail=f"Empresa com ID {update_data['id_empresa']} não encontrada.")
    
    for key, value in update_data.items():
        setattr(db_faturamento, key, value)
    
    db.commit()
    db.refresh(db_faturamento)
    return db_faturamento
    

@router.put("/produtos_vendidos/{id_venda}", response_model=api_schemas.ProdutosVendidos)
def update_produtos_vendidos(id_venda: int, produto_data: api_schemas.ProdutosVendidosUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_produto = db.query(api_models.ProdutosVendidos).filter(api_models.ProdutosVendidos.id_venda == id_venda).first()
    if not db_produto:
        raise HTTPException(status_code=404, detail="Venda de produto não encontrada.")
    
    update_data = produto_data.model_dump(exclude_unset=True)
    if "id_faturamento" in update_data:
        faturamento_existe = db.query(api_models.Faturamento).filter(api_models.Faturamento.id_faturamento == update_data["id_faturamento"]).first()
        if not faturamento_existe:
            raise HTTPException(status_code=404, detail=f"Faturamento com ID {update_data['id_faturamento']} não encontrado.")
    
    for key, value in update_data.items():
        setattr(db_produto, key, value)
    
    db.commit()
    db.refresh(db_produto)
    return db_produto

@router.get("/produtos_vendidos/")
def read_produtos_vendidos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(api_models.ProdutosVendidos)
    produtos = db.execute(stmt).scalars().all()
    return produtos


@router.get("/faturamento_mensal_por_empresa/")
def get_faturamento_mensal(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(api_models.Empresas.nome_empresa, api_models.Faturamento.faturamento_mensal).join(api_models.Faturamento)
    faturamento_mensal = db.execute(stmt).all()
    faturamento_mensal_list = []
    for empresa, faturamento in faturamento_mensal:
        faturamento_mensal_list.append({"nome_empresa": empresa, "faturamento_mensal": faturamento})
    return faturamento_mensal_list


@router.get("/media_notas_diretor/")
def get_media_notas_diretor(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(api_models.Empresas.diretor_empresa, func.avg(api_models.AvaliacoesDiretorEmpresa.nota_diretor).label("media_nota")).join(api_models.AvaliacoesDiretorEmpresa).group_by(api_models.Empresas.diretor_empresa)
    notas = db.execute(stmt).all()
    notas_list = []
    for diretor, media in notas:
        notas_list.append({"diretor_empresa": diretor, "media_nota": media})
    return notas_list