import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import MenuLateral from '../componentes/MenuLateral'
import CartaoBaia from '../componentes/CartaoBaia'
import { buscarRelatorios, buscarRelatorio } from '../servicos/api'
import './PaginaPainel.css'

function IconeMenu() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <line x1="3" y1="6"  x2="21" y2="6"  />
      <line x1="3" y1="12" x2="21" y2="12" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </svg>
  )
}

function LogoPatinha() {
  return (
    <svg width="34" height="34" viewBox="0 0 54 54" fill="none">
      <rect width="54" height="54" rx="14" fill="rgba(0,212,200,0.15)" />
      <ellipse cx="27" cy="33" rx="9" ry="7.5" fill="#00d4c8" />
      <ellipse cx="14.5" cy="27" rx="3.5" ry="4.5" transform="rotate(-15 14.5 27)" fill="#00d4c8" />
      <ellipse cx="20.5" cy="22" rx="3.2" ry="4.2" transform="rotate(-5 20.5 22)"  fill="#00d4c8" />
      <ellipse cx="33.5" cy="22" rx="3.2" ry="4.2" transform="rotate(5 33.5 22)"   fill="#00d4c8" />
      <ellipse cx="39.5" cy="27" rx="3.5" ry="4.5" transform="rotate(15 39.5 27)"  fill="#00d4c8" />
    </svg>
  )
}

const BAIAS_PADRAO = [
  { numero: 1, pet: { nome: 'Luna', tipo: 'gato', raca: 'Persa', idade: '3 anos', peso: '3.8 kg', tutor: 'Maria Silva', telefone: '(11) 99999-9999', motivo: 'Pós-operatório', diagnostico: 'Castração realizada com sucesso', medicamentos: 'Antibiótico 2x ao dia', alergias: 'Nenhuma', veterinario: 'Dra. Ana', dataEntrada: '2026-05-18' }, temDados: true  },
  { numero: 2, pet: { nome: 'Scout', tipo: 'cachorro', raca: 'Labrador', idade: '2 anos', peso: '28 kg', tutor: 'João Pereira', telefone: '(11) 98888-8888', motivo: 'Observação pós-trauma', diagnostico: 'Trauma leve, sem fraturas', medicamentos: 'Anti-inflamatório', alergias: 'Penicilina', veterinario: 'Dr. Carlos', dataEntrada: '2026-05-21' }, temDados: false },
  { numero: 3, pet: null, temDados: false },
  { numero: 4, pet: null, temDados: false },
  { numero: 5, pet: null, temDados: false },
  { numero: 6, pet: null, temDados: false },
]

function carregarBaias() {
  const salvas = localStorage.getItem('vetvision-baias')
  if (salvas) return JSON.parse(salvas)
  localStorage.setItem('vetvision-baias', JSON.stringify(BAIAS_PADRAO))
  return BAIAS_PADRAO
}

function resolverStatus(relatorio) {
  if (!relatorio) return 'descansando'
  if (relatorio.alertas?.length > 0) return 'alerta'
  return 'descansando'
}

function ultimaRefeicao(relatorio) {
  const refeicoes = relatorio?.refeicoes ?? []
  if (!refeicoes.length) return null
  return refeicoes[refeicoes.length - 1].inicio
}

export default function PaginaPainel() {
  const [menuAberto, setMenuAberto] = useState(false)
  const [baias, setBaias]           = useState([])
  const [relatorio, setRelatorio]   = useState(null)
  const [carregando, setCarregando] = useState(true)
  const navegar = useNavigate()

  useEffect(() => {
    setBaias(carregarBaias())
    async function carregar() {
      try {
        const lista = await buscarRelatorios()
        if (lista.length > 0) {
          const dados = await buscarRelatorio(lista[0])
          setRelatorio(dados)
        }
      } finally {
        setCarregando(false)
      }
    }
    carregar()
  }, [])

  function abrirDetalhesBaia(baia) {
    navegar(`/baia/${baia.numero}`, {
      state: { baia, relatorio: baia.temDados ? relatorio : null },
    })
  }

  return (
    <div className="pagina-painel">

      <header className="barra-topo">
        <div className="topo-esquerda">
          <button className="botao-menu" onClick={() => setMenuAberto(!menuAberto)}>
            <IconeMenu />
          </button>
          <div className="marca-topo">
            <LogoPatinha />
            <span>VetVision</span>
          </div>
        </div>
        <div className="topo-direita">
          <div className="avatar">
            {(localStorage.getItem('vetvision-usuario') ?? 'U')[0].toUpperCase()}
          </div>
        </div>
      </header>

      <MenuLateral aberto={menuAberto} onFechar={() => setMenuAberto(false)} />

      {menuAberto && (
        <div className="overlay-menu" onClick={() => setMenuAberto(false)} />
      )}

      <main className="conteudo-principal">

        <div className="painel-titulo">
          <div>
            <h2>Monitoramento de Baias</h2>
            <span className="painel-subtitulo">Clique no olho para ver os detalhes de cada baia</span>
          </div>
          <button className="botao-novo-animal" onClick={() => navegar('/cadastro')}>
            + Novo Animal
          </button>
        </div>

        {carregando ? (
          <p className="estado-mensagem">Carregando...</p>
        ) : (
          <div className="grade-baias">
            {baias.map((baia) => (
              <CartaoBaia
                key={baia.numero}
                numero={baia.numero}
                pet={baia.pet}
                status={!baia.pet ? 'vazia' : baia.temDados ? resolverStatus(relatorio) : 'descansando'}
                ultimaRefeicao={baia.temDados ? ultimaRefeicao(relatorio) : null}
                onVerDetalhes={() => abrirDetalhesBaia(baia)}
              />
            ))}
          </div>
        )}

      </main>

    </div>
  )
}
