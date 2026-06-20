import { createRoot } from 'react-dom/client';
import './styles/global.css';
import { App } from './app/App';

const root = document.getElementById('root');

if (!root) {
  throw new Error('Root element #root was not found.');
}

createRoot(root).render(<App />);

