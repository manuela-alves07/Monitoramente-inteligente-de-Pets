import './CartaoBaia.css'

function IconeOlho() {
  return (
    <svg width="19" height="19" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

const CORES_STATUS = {
  comendo:    { cor: '#00d4c8', label: 'Comendo'                },
  aguardando: { cor: '#4a6a8a', label: 'Aguardando monitoramento' },
  alerta:     { cor: '#ff8080', label: 'Alerta'                 },
  vazia:      { cor: '#2a3a50', label: 'Vazia'                  },
}

export default function CartaoBaia({ numero, pet, status, ultimaRefeicao, onVerDetalhes }) {
  const vazia   = status === 'vazia'
  const config  = CORES_STATUS[status] ?? CORES_STATUS.vazia

  return (
    <div className={`cartao-baia ${vazia ? 'cartao-baia--vazia' : ''}`}>

      <div className="baia-topo">
        <span className="baia-numero">Baia {String(numero).padStart(2, '0')}</span>
        {!vazia && (
          <span className="baia-status" style={{ color: config.cor }}>
            <span className="baia-bolinha" style={{ background: config.cor }} />
            {config.label}
          </span>
        )}
      </div>

      <div className="baia-pet">
        {vazia ? (
          <span className="baia-vazia-texto">— Vazia —</span>
        ) : (
          <>
            <span className="baia-emoji">
              {{ gato: '🐱', cachorro: '🐶', coelho: '🐰', passaro: '🐦' }[pet?.tipo] ?? '🐾'}
            </span>
            <span className="baia-nome">{pet?.nome ?? 'Pet'}</span>
          </>
        )}
      </div>

      {!vazia && (
        <div className="baia-rodape">
          <span className="baia-ultima">
            Última refeição: <strong>{ultimaRefeicao ?? '—'}</strong>
          </span>
        </div>
      )}

      <button className="botao-olho" onClick={onVerDetalhes} title="Ver detalhes">
        <IconeOlho />
      </button>

    </div>
  )
}
