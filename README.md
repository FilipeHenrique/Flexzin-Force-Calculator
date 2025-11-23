# 🏆 Flexzin Force — Sistema de Avaliação de Força de Jogadores de Xadrez

O **Flexzin Force (FF)** é um sistema criado para medir a força relativa de um jogador em comparação ao **Flexzin**.

O FF gera um índice onde:

- **1.0** → mesmo nível do Flexzin  
- **> 1.0** → jogador mais forte  
- **< 1.0** → jogador mais fraco  

📄 **Documento oficial completo (PDF):**  
[Flexzin Force.pdf](docs/FlexzinForce.pdf)

---

## 📌 Funcionalidades do Projeto

- Obtém partidas recentes de qualquer jogador (API Chess.com)  
- Separa e organiza partidas por ritmo: `rapid`, `blitz`, `bullet`  
- Calcula:
  - média de rating  
  - consistência (desvio padrão)  
  - margem de erro  
  - índice Flexzin Force por ritmo  
- Compara o jogador diretamente com o Flexzin  
- Retorna valores numéricos e interpretações claras  

---

## 📊 Interpretação dos Resultados

| FF | Interpretação |
|----|--------------|
| `< 0.7` | Superioridade absoluta do Flexzin |
| `0.7 – 0.85` | Vantagem clara do Flexzin |
| `0.85 – 0.95` | Ligeira vantagem do Flexzin |
| `0.95 – 1.05` | Equilíbrio |
| `1.05 – 1.15` | Jogador um pouco superior |
| `1.15 – 1.3` | Jogador claramente superior |https://github.com/FilipeHenrique/Flexzin-Force-Calculator
| `> 1.3` | Superioridade adversa |

---

## 🚀 Como rodar o projeto

```bash
git clone https://github.com/FilipeHenrique/Flexzin-Force-Calculator
python main.py
```