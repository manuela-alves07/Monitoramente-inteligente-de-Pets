import './PainelIlustracao.css'

export default function PainelIlustracao() {
  return (
    <div className="painel-ilustracao">
      <img
        src="/clinica-vetvision.png"
        alt="Clínica VetVision com monitoramento inteligente"
        className="imagem-clinica"
      />
      <div className="overlay" />
    </div>
  )
}
