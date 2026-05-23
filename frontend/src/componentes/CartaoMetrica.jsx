import './CartaoMetrica.css'

export default function CartaoMetrica({ icone, rotulo, valor, destaque }) {
  return (
    <div className={`cartao-metrica ${destaque ? 'cartao-metrica--destaque' : ''}`}>
      <span className="metrica-icone">{icone}</span>
      <strong className="metrica-valor">{valor}</strong>
      <small className="metrica-rotulo">{rotulo}</small>
    </div>
  )
}
