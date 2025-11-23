export default function ModuleSlot({ name, note }) {
  return (
    <div
      style={{
        border: '1px dashed #bbb',
        borderRadius: 8,
        padding: 12,
        background: '#fafafa',
        color: '#555',
        margin: '8px 0'
      }}
    >
      <div style={{ fontWeight: 600 }}>Module: {name}</div>
      {note && <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>{note}</div>}
    </div>
  )
}


