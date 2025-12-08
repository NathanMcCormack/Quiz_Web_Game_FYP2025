import { StrictMode } from 'react' //react wrapper used for to ctach potential problems by runnig things  multiple times. Used in Development only, does not affect behaviour
import { createRoot } from 'react-dom/client' //createRoot - newest way of starting a react app 
import './index.css' //global CSS 
import App from './App.jsx' //Main React component

createRoot(document.getElementById('root')).render( //looks inside index.html for teh route div, .render tells react what to showinside that route
  <StrictMode>
    <App />
  </StrictMode>,
)
