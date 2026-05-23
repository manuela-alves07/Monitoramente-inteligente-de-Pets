import { BrowserRouter, Routes, Route } from 'react-router-dom'
import PaginaLogin from './paginas/PaginaLogin'
import PaginaPainel from './paginas/PaginaPainel'
import PaginaDetalhesPet from './paginas/PaginaDetalhesPet'
import PaginaCadastroPet from './paginas/PaginaCadastroPet'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"             element={<PaginaLogin />} />
        <Route path="/painel"       element={<PaginaPainel />} />
        <Route path="/baia/:numero" element={<PaginaDetalhesPet />} />
        <Route path="/cadastro"     element={<PaginaCadastroPet />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
