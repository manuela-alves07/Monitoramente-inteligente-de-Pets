import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import MenuLateral from '../componentes/MenuLateral'
import CartaoBaia from '../componentes/CartaoBaia'
import { listarBaias } from '../servicos/api'
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

function formatarHora(iso) {
  if (!iso) return null
  const data = new Date(iso)
  const hoje = new Date()
  const ontem = new Date(hoje)
  ontem.setDate(hoje.getDate() - 1)
  const hora = data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  if (data.toDateString() === hoje.toDateString()) return `Hoje às ${hora}`
  if (data.toDateString() === ontem.toDateString()) return `Ontem às ${hora}`
  return data.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }) + ` às ${hora}`
}

function mapearBaia(b) {
  const temPet = b.id_animal && b.status_internacao === 'internado'
  return {
    id_baia:        b.id_baia,
    numero:         b.numero,
    temDados:       false,
    ultimaRefeicao: formatarHora(b.ultima_refeicao),
    ultimaAgua:     formatarHora(b.ultima_agua),
    pet: temPet ? {
      id:          b.id_animal,
      nome:        b.nome,
      tipo:        b.especie,
      raca:        b.raca || '—',
      tutor:       b.tutor,
      dataEntrada: b.data_entrada ? b.data_entrada.slice(0, 10) : '',
    } : null,
  }
}

function carregarConfig() {
  const salva = localStorage.getItem('vetvision-config')
  if (salva) return JSON.parse(salva)
  return { nomeClinica: '', colunas: 3 }
}


export default function PaginaPainel() {
  const [menuAberto, setMenuAberto]         = useState(false)
  const [dropdownAberto, setDropdownAberto] = useState(false)
  const [baias, setBaias]                   = useState([])
  const [carregando, setCarregando]         = useState(true)
  const [config]                            = useState(carregarConfig)
  const navegar = useNavigate()

  const nomeUsuario = localStorage.getItem('vetvision-usuario') ?? 'Usuário'
  const loginUsuario = localStorage.getItem('vetvision-login') ?? ''
  const roleUsuario  = localStorage.getItem('vetvision-role') ?? 'user'

  function logout() {
    localStorage.removeItem('vetvision-usuario')
    localStorage.removeItem('vetvision-login')
    localStorage.removeItem('vetvision-role')
    localStorage.removeItem('vetvision-id-usuario')
    navegar('/')
  }

  useEffect(() => {
    async function carregar() {
      try {
        const baiasDB = await listarBaias()
        setBaias(baiasDB.map(mapearBaia))
      } finally {
        setCarregando(false)
      }
    }
    carregar()
  }, [])

  function abrirDetalhesBaia(baia) {
    navegar(`/baia/${baia.numero}`, {
      state: { baia, relatorio: null },
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
            <span>{config.nomeClinica || 'VetVision'}</span>
          </div>
        </div>
        <div className="topo-direita">
          <div className="avatar-wrapper">
            <button className="avatar" onClick={() => setDropdownAberto(d => !d)}>
              {nomeUsuario[0].toUpperCase()}
            </button>
            {dropdownAberto && (
              <div className="avatar-dropdown">
                <div className="dropdown-info">
                  <strong>{nomeUsuario}</strong>
                  <span>{loginUsuario}</span>
                  <span className="dropdown-role">{roleUsuario === 'admin' ? 'Administrador' : 'Usuário'}</span>
                </div>
                <hr className="dropdown-divisor" />
                <button className="dropdown-item" onClick={() => { setDropdownAberto(false); navegar('/perfil') }}>
                  Alterar senha
                </button>
                <button className="dropdown-item dropdown-item--sair" onClick={logout}>
                  Sair
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <MenuLateral aberto={menuAberto} onFechar={() => setMenuAberto(false)} />

      {menuAberto && (
        <div className="overlay-menu" onClick={() => setMenuAberto(false)} />
      )}
      {dropdownAberto && (
        <div className="overlay-menu overlay-menu--transparente" onClick={() => setDropdownAberto(false)} />
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
          <div className="grade-baias" style={{ gridTemplateColumns: `repeat(${config.colunas}, 1fr)` }}>
            {baias.map((baia) => (
              <CartaoBaia
                key={baia.numero}
                numero={baia.numero}
                pet={baia.pet}
                status={!baia.pet ? 'vazia' : (baia.ultimaRefeicao || baia.ultimaAgua) ? 'monitorado' : 'aguardando'}
                ultimaRefeicao={baia.ultimaRefeicao}
                ultimaAgua={baia.ultimaAgua}
                onVerDetalhes={() => abrirDetalhesBaia(baia)}
              />
            ))}
          </div>
        )}

      </main>

    </div>
  )
}
