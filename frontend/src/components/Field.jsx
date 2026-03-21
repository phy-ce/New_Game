import { useState, useRef, useEffect } from 'react';
import { useGame } from '../context/GameContext';
import UnitCard from './UnitCard';
import '../styles/Field.css';

const SLOT_LIMIT = 7;

export default function Field({ units, isMe, onTargetUnit }) {
  const { unitTemplates } = useGame();
  const [expandedStack, setExpandedStack] = useState(null);
  const prevIdsRef = useRef(new Set());
  const [newIds, setNewIds] = useState(new Set());

  useEffect(() => {
    const currentIds = new Set(units.map(u => u.id));
    const added = new Set([...currentIds].filter(id => !prevIdsRef.current.has(id)));
    if (added.size > 0) {
      setNewIds(added);
      const timer = setTimeout(() => setNewIds(new Set()), 400);
      prevIdsRef.current = currentIds;
      return () => clearTimeout(timer);
    }
    prevIdsRef.current = currentIds;
  }, [units]);

  const shouldStack = units.length > SLOT_LIMIT;

  if (!shouldStack) {
    return (
      <div className={`field ${isMe ? 'field-me' : 'field-opponent'}`}>
        {units.map(unit => (
          <UnitCard
            key={unit.id}
            unit={unit}
            isNew={newIds.has(unit.id)}
            onTarget={onTargetUnit ? () => onTargetUnit(unit.id) : undefined}
          />
        ))}
      </div>
    );
  }

  const stacks = {};
  for (const unit of units) {
    if (!stacks[unit.name]) stacks[unit.name] = [];
    stacks[unit.name].push(unit);
  }
  const stackEntries = Object.entries(stacks);
  const visible = stackEntries.slice(0, SLOT_LIMIT);
  const overflow = stackEntries.length - SLOT_LIMIT;

  return (
    <div className={`field ${isMe ? 'field-me' : 'field-opponent'}`}>
      {visible.map(([name, unitList]) => (
        <div
          key={name}
          className="unit-stack-slot"
          onClick={() => setExpandedStack(expandedStack === name ? null : name)}
        >
          <UnitCard unit={unitList[0]} stackCount={unitList.length} isNew={newIds.has(unitList[0].id)} />
          {expandedStack === name && (
            <div className="stack-popup">
              {unitList.map(u => (
                <div key={u.id} className="stack-unit-row">
                  {u.name} — ♥ {u.current_hp}/{unitTemplates[u.name]?.hp}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
      {overflow > 0 && (
        <div className="stack-overflow">+{overflow} more</div>
      )}
    </div>
  );
}
