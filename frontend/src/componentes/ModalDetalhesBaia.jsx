import './ModalDetalhesBaia.css'

function IconeFechar() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6"  y1="6" x2="18" y2="18" />
    </svg>
  )
}

export default function ModalDetalhesBaia({ baia, relatorio, onFechar }) {
  if (!baia || !relatorio) return null

  const refeicoes = relatorio.refeicoes ?? []
  const cheiradas = relatorio.cheiradas ?? []
  const alertas   = relatorio.alertas   ?? []

  const duracaoTotal = refeicoes.reduce((soma, r) => soma + r.duracao_s, 0)

  return (
    <div className="modal-overlay" onClick={onFechar}>
      <div className="modal-caixa" onClick={(e) => e.stopPropagation()}>

        <div className="modal-cabecalho">
          <div>
            <h2>Baia {String(baia.numero).padStart(2, '0')} — {baia.pet?.nome}</h2>
            <span className="modal-data">{relatorio.data} · {relatorio.horario_inicio} – {relatorio.horario_fim}</span>
          </div>
          <button className="modal-botao-fechar" onClick={onFechar}>
            <IconeFechar />
          </button>
        </div>

        <div className="modal-metricas">
          <div className="modal-metrica">
            <strong>{refeicoes.length}</strong>
            <small>Refeições</small>
          </div>
          <div className="modal-metrica">
            <strong>{cheiradas.length}</strong>
            <small>Aproximações</small>
          </div>
          <div className="modal-metrica">
            <strong>{duracaoTotal >= 60 ? `${(duracaoTotal / 60).toFixed(1)} min` : `${duracaoTotal.toFixed(1)}s`}</strong>
            <small>Tempo comendo</small>
          </div>
          <div className="modal-metrica">
            <strong>{alertas.length}</strong>
            <small>Alertas</small>
          </div>
        </div>

        {alertas.length > 0 && (
          <div className="modal-secao">
            <h3>Alertas</h3>
            {alertas.map((alerta, i) => (
              <div key={i} className={`modal-alerta modal-alerta--${alerta.nivel}`}>
                {alerta.mensagem}
              </div>
            ))}
          </div>
        )}

        {refeicoes.length > 0 && (
          <div className="modal-secao">
            <h3>Refeições detectadas</h3>
            <table className="modal-tabela">
              <thead>
                <tr>
                  <th>Horário</th>
                  <th>Duração</th>
                </tr>
              </thead>
              <tbody>
                {refeicoes.map((r, i) => (
                  <tr key={i}>
                    <td>{r.inicio}</td>
                    <td>{r.duracao_s}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {refeicoes.length === 0 && alertas.length === 0 && (
          <p className="modal-vazio">Nenhum evento registrado neste período.</p>
        )}

      </div>
    </div>
  )
}
