import { useState } from 'react';
import { useGame } from '../context/GameContext';
import '../styles/UnitCard.css';

export default function UnitCard({ unit, stackCount }) {
  const { unitTemplates } = useGame();
  const [showInspector, setShowInspector] = useState(false);
  const template = unitTemplates[unit.name] || {};

  return (
    <div
      className="unit-card"
      onMouseEnter={() => setShowInspector(true)}
      onMouseLeave={() => setShowInspector(false)}
    >
      {stackCount > 1 && <div className="unit-stack-count">x{stackCount}</div>}
      <div className="unit-image">{unit.name.charAt(0)}</div>
      <div className="unit-name">{unit.name}</div>
      <div className="unit-stats">
        <span className="unit-hp">♥ {unit.current_hp}/{template.hp}</span>
        <span className="unit-attack">⚔ {template.attack}</span>
      </div>

      {showInspector && (
        <div className="unit-inspector">
          <div className="ui-name">{unit.name}</div>
          <div className="ui-stat">HP: {unit.current_hp}/{template.hp}</div>
          <div className="ui-stat">ATK: {template.attack}</div>
          <div className="ui-desc">{template.description}</div>
        </div>
      )}
    </div>
  );
}
