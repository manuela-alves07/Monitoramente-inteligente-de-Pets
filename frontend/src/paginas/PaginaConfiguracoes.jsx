import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './PaginaConfiguracoes.css'

function IconeVoltar() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  )
}

function carregarConfig() {
  const salva = localStorage.getItem('vetvision-config')
  if (salva) return JSON.parse(salva)
  return { nomeClinica: '', colunas: 3 }
}

function carregarBaias() {
  const salvas = localStorage.getItem('vetvision-baias')
  if (salvas) return JSON.parse(salvas)
  return Array.from({ length: 6 }, (_, i) => ({ numero: i + 1, pet: null, temDados: false }))
}

export default function PaginaConfiguracoes() {
  const navegar = useNavigate()

  const [config, setConfig] = useState(carregarConfig)
  const [baias, setBaias]   = useState(carregarBaias)
  const [salvo, setSalvo]   = useState(false)

  function atualizarConfig(campo, valor) {
    setConfig(prev => ({ ...prev, [campo]: valor }))
    setSalvo(false)
  }

  function adicionarBaia() {
    const proximoNumero = baias.length > 0 ? Math.max(...baias.map(b => b.numero)) + 1 : 1
    const novasBaias = [...baias, { numero: proximoNumero, pet: null, temDados: false }]
    setBaias(novasBaias)
    setSalvo(false)
  }

  function removerBaia(numero) {
    const baia = baias.find(b => b.numero === numero)
    if (baia?.pet) return
    setBaias(prev => prev.filter(b => b.numero !== numero))
    setSalvo(false)
  }

  function salvar() {
    localStorage.setItem('vetvision-config', JSON.stringify(config))
    localStorage.setItem('vetvision-baias', JSON.stringify(baias))
    setSalvo(true)
    setTimeout(() => setSalvo(false), 2000)
  }

  return (
    <div className="pagina-config">

      <header className="config-cabecalho">
        <button className="botao-voltar-config" onClick={() => navegar('/painel')}>
          <IconeVoltar /> Voltar ao Painel
        </button>
        <h1>Configurações</h1>
      </header>

      <main className="config-conteudo">

        <div className="config-secao">
          <h2>Informações da Clínica</h2>
          <div className="config-campo">
            <label>Nome da clínica</label>
            <input
              type="text"
              placeholder="Ex: Clínica Vet São Paulo"
              value={config.nomeClinica}
              onChange={e => atualizarConfig('nomeClinica', e.target.value)}
            />
          </div>
        </div>

        <div className="config-secao">
          <h2>Layout do Painel</h2>
          <p className="config-descricao">Escolha quantas baias aparecem por linha no painel.</p>
          <div className="config-colunas">
            {[2, 3, 4].map(n => (
              <button
                key={n}
                className={`botao-coluna ${config.colunas === n ? 'botao-coluna--ativo' : ''}`}
                onClick={() => atualizarConfig('colunas', n)}
              >
                {n} colunas
              </button>
            ))}
          </div>
        </div>

        <div className="config-secao">
          <div className="config-secao-topo">
            <div>
              <h2>Baias</h2>
              <p className="config-descricao">Gerencie as baias da clínica. Baias ocupadas não podem ser removidas.</p>
            </div>
            <button className="botao-add-baia" onClick={adicionarBaia}>
              + Nova Baia
            </button>
          </div>

          <div className="lista-baias-config">
            {baias.map(baia => (
              <div key={baia.numero} className="item-baia-config">
                <div className="baia-config-info">
                  <span className="baia-config-numero">Baia {String(baia.numero).padStart(2, '0')}</span>
                  {baia.pet
                    ? <span className="baia-config-status baia-config-status--ocupada">Ocupada — {baia.pet.nome}</span>
                    : <span className="baia-config-status baia-config-status--vazia">Vazia</span>
                  }
                </div>
                <button
                  className="botao-remover-baia"
                  onClick={() => removerBaia(baia.numero)}
                  disabled={!!baia.pet}
                  title={baia.pet ? 'Remova o animal antes de excluir a baia' : 'Remover baia'}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="config-acoes">
          <button className="botao-salvar-config" onClick={salvar}>
            {salvo ? '✓ Salvo!' : 'Salvar configurações'}
          </button>
        </div>

      </main>
    </div>
  )
}
