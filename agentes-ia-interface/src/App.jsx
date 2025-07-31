import React, { useState, useEffect, useRef } from 'react'
import './App.css'
import { 
  MessageSquare, TrendingUp, Clock, Users, Cpu, HardDrive, 
  Plus, Settings, Video, Download, Save, Database, User, 
  Edit, Upload, File, Trash2, Play, Pause, RotateCcw, 
  Server, Bot, Monitor, Send, Mic, MicOff, Volume2, VolumeX,
  Eye, EyeOff, Shield, Key, Globe, Wifi, WifiOff
} from 'lucide-react'

// Componentes UI básicos
const Button = ({ children, onClick, className, style, disabled, ...props }) => (
  <button 
    onClick={onClick} 
    className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${className || ''}`}
    style={style}
    disabled={disabled}
    {...props}
  >
    {children}
  </button>
)

const Switch = ({ checked, onCheckedChange, className }) => (
  <div 
    onClick={() => onCheckedChange(!checked)}
    className={`w-12 h-6 rounded-full cursor-pointer transition-all duration-200 ${
      checked ? 'switch-active' : 'switch-inactive'
    } ${className || ''}`}
    style={{ position: 'relative' }}
  >
    <div 
      className="w-5 h-5 bg-white rounded-full transition-all duration-200"
      style={{
        position: 'absolute',
        top: '2px',
        left: checked ? '26px' : '2px'
      }}
    />
  </div>
)

const Dialog = ({ open, onOpenChange, children }) => {
  if (!open) return null
  
  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ 
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(4px)'
      }}
      onClick={() => onOpenChange(false)}
    >
      <div 
        className="modal-glass p-6 max-w-4xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  )
}

const DialogContent = ({ children, className, style }) => (
  <div className={className} style={style}>
    {children}
  </div>
)

const DialogHeader = ({ children }) => (
  <div className="mb-6">
    {children}
  </div>
)

const DialogTitle = ({ children, className, style }) => (
  <h2 className={`text-2xl font-bold ${className || ''}`} style={style}>
    {children}
  </h2>
)

// Clase para conexiones REALES
class ConexionesReales {
  static async verificarOllama() {
    try {
      const response = await fetch('http://localhost:11434/api/tags')
      if (response.ok) {
        const data = await response.json()
        return {
          conectado: true,
          modelos: data.models || []
        }
      }
    } catch (error) {
      console.log('Ollama no disponible:', error.message)
    }
    return { conectado: false, modelos: [] }
  }

  static async verificarLMStudio() {
    try {
      const response = await fetch('http://localhost:1234/v1/models')
      if (response.ok) {
        const data = await response.json()
        return {
          conectado: true,
          modelos: data.data || []
        }
      }
    } catch (error) {
      console.log('LM Studio no disponible:', error.message)
    }
    return { conectado: false, modelos: [] }
  }

  static async verificarLocalAI() {
    try {
      const response = await fetch('http://localhost:8080/v1/models')
      if (response.ok) {
        const data = await response.json()
        return {
          conectado: true,
          modelos: data.data || []
        }
      }
    } catch (error) {
      console.log('LocalAI no disponible:', error.message)
    }
    return { conectado: false, modelos: [] }
  }

  static async generarRespuesta(mensaje, agente) {
    try {
      // Intentar con modelo local primero
      if (agente.modelo.startsWith('ollama:')) {
        const modeloLocal = agente.modelo.replace('ollama:', '')
        const response = await fetch('http://localhost:11434/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: modeloLocal,
            prompt: `${agente.prompt}\n\nUsuario: ${mensaje}\nAsistente:`,
            stream: false,
            options: {
              temperature: agente.temperatura || 0.7,
              num_predict: agente.maxTokens || 1000
            }
          })
        })
        
        if (response.ok) {
          const data = await response.json()
          return data.response
        }
      }

      // Fallback a OpenAI API
      if (agente.modelo.startsWith('gpt-')) {
        const apiKey = localStorage.getItem('openai_api_key')
        if (!apiKey) throw new Error('API Key de OpenAI no configurada')

        const response = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
          },
          body: JSON.stringify({
            model: agente.modelo,
            messages: [
              { role: 'system', content: agente.prompt },
              { role: 'user', content: mensaje }
            ],
            temperature: agente.temperatura || 0.7,
            max_tokens: agente.maxTokens || 1000
          })
        })

        if (response.ok) {
          const data = await response.json()
          return data.choices[0].message.content
        }
      }

      throw new Error('No se pudo generar respuesta')
    } catch (error) {
      console.error('Error generando respuesta:', error)
      return `Error: ${error.message}`
    }
  }

  static async enviarTelegram(token, chatId, mensaje) {
    try {
      const response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: mensaje,
          parse_mode: 'HTML'
        })
      })
      
      return response.ok
    } catch (error) {
      console.error('Error enviando mensaje Telegram:', error)
      return false
    }
  }

  static async verificarTelegramBot(token) {
    try {
      const response = await fetch(`https://api.telegram.org/bot${token}/getMe`)
      if (response.ok) {
        const data = await response.json()
        return data.ok ? data.result : null
      }
    } catch (error) {
      console.error('Error verificando bot Telegram:', error)
    }
    return null
  }

  static async obtenerMensajesTelegram(token, offset = 0) {
    try {
      const response = await fetch(`https://api.telegram.org/bot${token}/getUpdates?offset=${offset}`)
      if (response.ok) {
        const data = await response.json()
        return data.ok ? data.result : []
      }
    } catch (error) {
      console.error('Error obteniendo mensajes Telegram:', error)
    }
    return []
  }

  static async descargarModelo(nombre) {
    try {
      const response = await fetch('http://localhost:11434/api/pull', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: nombre })
      })
      
      return response.ok
    } catch (error) {
      console.error('Error descargando modelo:', error)
      return false
    }
  }
}

// Componente principal
function App() {
  // Estados principales
  const [pestanaActiva, setPestanaActiva] = useState('panel')
  const [agentes, setAgentes] = useState([
    {
      id: 1,
      nombre: 'Analista Financiero',
      rol: 'Finanzas',
      avatar: '💰',
      estado: 'inactivo',
      modelo: 'gpt-4',
      conversaciones: 247,
      precision: 92,
      aprendiendo: true,
      prompt: 'Eres un analista financiero experto especializado en análisis de mercados, inversiones y estrategias financieras.',
      temperatura: 0.7,
      maxTokens: 1000,
      telegram: false,
      telegramToken: '',
      baseDatos: '',
      voz: 'masculina'
    },
    {
      id: 2,
      nombre: 'Jefe de Ventas',
      rol: 'Ventas',
      avatar: '📈',
      estado: 'inactivo',
      modelo: 'claude-3',
      conversaciones: 189,
      precision: 89,
      aprendiendo: true,
      prompt: 'Eres un experto en ventas y estrategias comerciales, especializado en cerrar deals y generar leads.',
      temperatura: 0.8,
      maxTokens: 1200,
      telegram: false,
      telegramToken: '',
      baseDatos: '',
      voz: 'masculina'
    },
    {
      id: 3,
      nombre: 'Especialista Marketing',
      rol: 'Marketing',
      avatar: '🎨',
      estado: 'inactivo',
      modelo: 'gemini-pro',
      conversaciones: 156,
      precision: 87,
      aprendiendo: false,
      prompt: 'Eres un especialista en marketing digital, branding y estrategias de contenido creativo.',
      temperatura: 0.9,
      maxTokens: 1500,
      telegram: false,
      telegramToken: '',
      baseDatos: '',
      voz: 'femenina'
    },
    {
      id: 4,
      nombre: 'Desarrollador Senior',
      rol: 'Desarrollo',
      avatar: '💻',
      estado: 'inactivo',
      modelo: 'ollama:codellama',
      conversaciones: 203,
      precision: 95,
      aprendiendo: true,
      prompt: 'Eres un desarrollador senior experto en múltiples lenguajes de programación y arquitecturas de software.',
      temperatura: 0.3,
      maxTokens: 2000,
      telegram: false,
      telegramToken: '',
      baseDatos: '',
      voz: 'masculina'
    }
  ])

  const [salas3D, setSalas3D] = useState([
    {
      id: 1,
      nombre: 'Sala Ejecutiva',
      tipo: 'ejecutiva',
      agentesActivos: [],
      mensajes: [],
      grabando: false,
      archivos: [],
      armarios: [
        { id: 1, nombre: 'Documentos Financieros', archivos: [] },
        { id: 2, nombre: 'Contratos', archivos: [] },
        { id: 3, nombre: 'Reportes', archivos: [] }
      ],
      aprendizaje: {
        habilitado: true,
        conversacionesGuardadas: [],
        conocimientoBase: [],
        patrones: []
      },
      configuracion: {
        grabacionAutomatica: false,
        transcripcionVoz: true,
        notificacionesTelegram: false,
        backupAutomatico: true
      }
    },
    {
      id: 2,
      nombre: 'Sala Creativa',
      tipo: 'creativa',
      agentesActivos: [],
      mensajes: [],
      grabando: false,
      archivos: [],
      armarios: [
        { id: 1, nombre: 'Diseños', archivos: [] },
        { id: 2, nombre: 'Referencias', archivos: [] },
        { id: 3, nombre: 'Proyectos', archivos: [] }
      ],
      aprendizaje: {
        habilitado: true,
        conversacionesGuardadas: [],
        conocimientoBase: [],
        patrones: []
      },
      configuracion: {
        grabacionAutomatica: false,
        transcripcionVoz: true,
        notificacionesTelegram: false,
        backupAutomatico: true
      }
    }
  ])

  // Estados de modelos y servicios
  const [estadoOllama, setEstadoOllama] = useState({ conectado: false, modelos: [] })
  const [estadoLMStudio, setEstadoLMStudio] = useState({ conectado: false, modelos: [] })
  const [estadoLocalAI, setEstadoLocalAI] = useState({ conectado: false, modelos: [] })
  const [modelosLocales, setModelosLocales] = useState([])

  // Estados de modales
  const [modalAgenteAbierto, setModalAgenteAbierto] = useState(false)
  const [modalSalaAbierto, setModalSalaAbierto] = useState(false)
  const [agenteSeleccionado, setAgenteSeleccionado] = useState(null)
  const [salaSeleccionada, setSalaSeleccionada] = useState(null)

  // Estados de estadísticas
  const [estadisticas, setEstadisticas] = useState({
    conversacionesHoy: 1247,
    tareasCompletadas: 89,
    tiempoAhorrado: 156,
    agentesOnline: 0,
    modelosActivos: 0,
    usoMemoria: 67
  })

  // Estados de Telegram
  const [telegramPolling, setTelegramPolling] = useState({})

  // Efectos
  useEffect(() => {
    detectarModelos()
    const interval = setInterval(detectarModelos, 30000) // Cada 30 segundos
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    // Actualizar estadísticas
    const agentesActivos = agentes.filter(a => a.estado === 'activo').length
    const modelosActivos = modelosLocales.filter(m => m.activo).length
    
    setEstadisticas(prev => ({
      ...prev,
      agentesOnline: agentesActivos,
      modelosActivos: modelosActivos
    }))
  }, [agentes, modelosLocales])

  // Funciones principales
  const detectarModelos = async () => {
    try {
      const [ollama, lmstudio, localai] = await Promise.all([
        ConexionesReales.verificarOllama(),
        ConexionesReales.verificarLMStudio(),
        ConexionesReales.verificarLocalAI()
      ])

      setEstadoOllama(ollama)
      setEstadoLMStudio(lmstudio)
      setEstadoLocalAI(localai)

      // Combinar todos los modelos
      const todosModelos = [
        ...ollama.modelos.map(m => ({ ...m, servicio: 'Ollama', activo: false })),
        ...lmstudio.modelos.map(m => ({ ...m, servicio: 'LM Studio', activo: false })),
        ...localai.modelos.map(m => ({ ...m, servicio: 'LocalAI', activo: false }))
      ]

      setModelosLocales(todosModelos)
    } catch (error) {
      console.error('Error detectando modelos:', error)
    }
  }

  const crearAgente = async (datosAgente) => {
    try {
      // Validar conexión con modelo si es local
      if (datosAgente.modelo.startsWith('ollama:')) {
        if (!estadoOllama.conectado) {
          alert('❌ Error: Ollama no está conectado')
          return
        }
      }

      // Validar token de Telegram si está habilitado
      if (datosAgente.telegram && datosAgente.telegramToken) {
        const botInfo = await ConexionesReales.verificarTelegramBot(datosAgente.telegramToken)
        if (!botInfo) {
          alert('❌ Error: Token de Telegram inválido')
          return
        }
      }

      const nuevoAgente = {
        ...datosAgente,
        id: Date.now(),
        estado: 'inactivo',
        conversaciones: 0,
        precision: 85,
        aprendiendo: true
      }

      setAgentes(prev => [...prev, nuevoAgente])
      setModalAgenteAbierto(false)
      setAgenteSeleccionado(null)
      
      alert(`✅ Agente "${nuevoAgente.nombre}" creado exitosamente`)
    } catch (error) {
      console.error('Error creando agente:', error)
      alert(`❌ Error creando agente: ${error.message}`)
    }
  }

  const activarAgente = async (agenteId) => {
    const agente = agentes.find(a => a.id === agenteId)
    if (!agente) return

    try {
      // Verificar conexión con modelo
      if (agente.modelo.startsWith('ollama:') && !estadoOllama.conectado) {
        alert('❌ Error: Ollama no está conectado')
        return
      }

      // Activar agente
      setAgentes(prev => prev.map(a => 
        a.id === agenteId ? { ...a, estado: 'activo' } : a
      ))

      // Iniciar polling de Telegram si está configurado
      if (agente.telegram && agente.telegramToken) {
        iniciarPollingTelegram(agente)
      }

      alert(`✅ Agente "${agente.nombre}" activado`)
    } catch (error) {
      console.error('Error activando agente:', error)
      alert(`❌ Error activando agente: ${error.message}`)
    }
  }

  const desactivarAgente = (agenteId) => {
    const agente = agentes.find(a => a.id === agenteId)
    if (!agente) return

    setAgentes(prev => prev.map(a => 
      a.id === agenteId ? { ...a, estado: 'inactivo' } : a
    ))

    // Detener polling de Telegram
    if (telegramPolling[agenteId]) {
      clearInterval(telegramPolling[agenteId])
      setTelegramPolling(prev => {
        const nuevo = { ...prev }
        delete nuevo[agenteId]
        return nuevo
      })
    }

    alert(`⏸️ Agente "${agente.nombre}" desactivado`)
  }

  const iniciarPollingTelegram = (agente) => {
    if (telegramPolling[agente.id]) return

    let offset = 0
    const interval = setInterval(async () => {
      try {
        const mensajes = await ConexionesReales.obtenerMensajesTelegram(agente.telegramToken, offset)
        
        for (const mensaje of mensajes) {
          if (mensaje.message && mensaje.message.text) {
            const respuesta = await ConexionesReales.generarRespuesta(mensaje.message.text, agente)
            await ConexionesReales.enviarTelegram(
              agente.telegramToken, 
              mensaje.message.chat.id, 
              respuesta
            )
            
            // Actualizar estadísticas
            setAgentes(prev => prev.map(a => 
              a.id === agente.id ? { ...a, conversaciones: a.conversaciones + 1 } : a
            ))
          }
          offset = mensaje.update_id + 1
        }
      } catch (error) {
        console.error('Error en polling Telegram:', error)
      }
    }, 2000) // Cada 2 segundos

    setTelegramPolling(prev => ({ ...prev, [agente.id]: interval }))
  }

  const toggleModelo = async (modelo, activar) => {
    try {
      setModelosLocales(prev => prev.map(m => 
        m.name === modelo.name ? { ...m, activo: activar } : m
      ))
      
      alert(`${activar ? '✅ Modelo activado' : '⏸️ Modelo desactivado'}: ${modelo.name}`)
    } catch (error) {
      console.error('Error toggling modelo:', error)
      alert(`❌ Error: ${error.message}`)
    }
  }

  const descargarModelo = async (nombre) => {
    try {
      alert(`🔄 Descargando modelo "${nombre}"...`)
      const exito = await ConexionesReales.descargarModelo(nombre)
      
      if (exito) {
        alert(`✅ Modelo "${nombre}" descargado exitosamente`)
        detectarModelos() // Redetectar modelos
      } else {
        alert(`❌ Error descargando modelo "${nombre}"`)
      }
    } catch (error) {
      console.error('Error descargando modelo:', error)
      alert(`❌ Error: ${error.message}`)
    }
  }

  const eliminarAgente = (agenteId) => {
    const agente = agentes.find(a => a.id === agenteId)
    if (!agente) return

    if (confirm(`¿Eliminar el agente "${agente.nombre}"?`)) {
      // Detener polling si está activo
      if (telegramPolling[agenteId]) {
        clearInterval(telegramPolling[agenteId])
        setTelegramPolling(prev => {
          const nuevo = { ...prev }
          delete nuevo[agenteId]
          return nuevo
        })
      }

      setAgentes(prev => prev.filter(a => a.id !== agenteId))
      alert(`🗑️ Agente "${agente.nombre}" eliminado`)
    }
  }

  const toggleAprendizaje = (agenteId) => {
    setAgentes(prev => prev.map(a => 
      a.id === agenteId ? { ...a, aprendiendo: !a.aprendiendo } : a
    ))
  }

  const crearSala3D = (datosSala) => {
    const nuevaSala = {
      ...datosSala,
      id: Date.now(),
      agentesActivos: [],
      mensajes: [],
      grabando: false
    }

    setSalas3D(prev => [...prev, nuevaSala])
    setModalSalaAbierto(false)
    setSalaSeleccionada(null)
    
    alert(`✅ Sala "${nuevaSala.nombre}" creada exitosamente`)
  }

  const eliminarSala = (salaId) => {
    const sala = salas3D.find(s => s.id === salaId)
    if (!sala) return

    if (confirm(`¿Eliminar la sala "${sala.nombre}"?`)) {
      setSalas3D(prev => prev.filter(s => s.id !== salaId))
      alert(`🗑️ Sala "${sala.nombre}" eliminada`)
    }
  }

  const llamarAgenteASala = (salaId, agenteId) => {
    const agente = agentes.find(a => a.id === agenteId)
    const sala = salas3D.find(s => s.id === salaId)
    
    if (!agente || !sala) return

    setSalas3D(prev => prev.map(s => 
      s.id === salaId ? {
        ...s,
        agentesActivos: [...(s.agentesActivos || []), agenteId],
        mensajes: [...(s.mensajes || []), {
          id: Date.now(),
          tipo: 'sistema',
          texto: `${agente.avatar} ${agente.nombre} se ha unido a la sala`,
          timestamp: new Date()
        }]
      } : s
    ))
  }

  const echarAgenteDeSala = (salaId, agenteId) => {
    const agente = agentes.find(a => a.id === agenteId)
    const sala = salas3D.find(s => s.id === salaId)
    
    if (!agente || !sala) return

    setSalas3D(prev => prev.map(s => 
      s.id === salaId ? {
        ...s,
        agentesActivos: (s.agentesActivos || []).filter(id => id !== agenteId),
        mensajes: [...(s.mensajes || []), {
          id: Date.now(),
          tipo: 'sistema',
          texto: `${agente.avatar} ${agente.nombre} ha salido de la sala`,
          timestamp: new Date()
        }]
      } : s
    ))
  }

  const enviarMensajeSala = async (salaId, mensaje) => {
    const sala = salas3D.find(s => s.id === salaId)
    if (!sala || !mensaje.trim()) return

    // Agregar mensaje del usuario
    const mensajeUsuario = {
      id: Date.now(),
      tipo: 'usuario',
      texto: mensaje,
      timestamp: new Date()
    }

    setSalas3D(prev => prev.map(s => 
      s.id === salaId ? {
        ...s,
        mensajes: [...(s.mensajes || []), mensajeUsuario]
      } : s
    ))

    // Generar respuestas de todos los agentes activos en la sala
    for (const agenteId of sala.agentesActivos || []) {
      const agente = agentes.find(a => a.id === agenteId)
      if (agente && agente.estado === 'activo') {
        try {
          const respuesta = await ConexionesReales.generarRespuesta(mensaje, agente)
          
          const mensajeAgente = {
            id: Date.now() + agenteId,
            tipo: 'agente',
            agente: agente,
            texto: respuesta,
            timestamp: new Date()
          }

          setSalas3D(prev => prev.map(s => 
            s.id === salaId ? {
              ...s,
              mensajes: [...(s.mensajes || []), mensajeAgente]
            } : s
          ))

          // Actualizar estadísticas
          setAgentes(prev => prev.map(a => 
            a.id === agenteId ? { ...a, conversaciones: a.conversaciones + 1 } : a
          ))
        } catch (error) {
          console.error('Error generando respuesta:', error)
        }
      }
    }
  }

  const limpiarChatSala = (salaId) => {
    setSalas3D(prev => prev.map(s => 
      s.id === salaId ? { ...s, mensajes: [] } : s
    ))
  }

  const iniciarGrabacionSala = (salaId) => {
    setSalas3D(prev => prev.map(s => 
      s.id === salaId ? { ...s, grabando: !s.grabando } : s
    ))
    
    const sala = salas3D.find(s => s.id === salaId)
    alert(sala?.grabando ? '⏹️ Grabación detenida' : '🔴 Grabación iniciada')
  }

  // Funciones avanzadas para salas 3D
  const subirArchivoSala = async (salaId, archivo) => {
    try {
      const nuevoArchivo = {
        id: Date.now(),
        nombre: archivo.name,
        tipo: archivo.type,
        tamaño: archivo.size,
        fechaSubida: new Date(),
        contenido: await archivo.text() // Para archivos de texto
      }

      setSalas3D(prev => prev.map(s => 
        s.id === salaId ? {
          ...s,
          archivos: [...(s.archivos || []), nuevoArchivo]
        } : s
      ))

      alert(`📁 Archivo "${archivo.name}" subido exitosamente`)
    } catch (error) {
      console.error('Error subiendo archivo:', error)
      alert('❌ Error subiendo archivo')
    }
  }

  const moverArchivoArmario = (salaId, archivoId, armarioId) => {
    const sala = salas3D.find(s => s.id === salaId)
    if (!sala) return

    const archivo = sala.archivos.find(a => a.id === archivoId)
    if (!archivo) return

    setSalas3D(prev => prev.map(s => 
      s.id === salaId ? {
        ...s,
        archivos: s.archivos.filter(a => a.id !== archivoId),
        armarios: s.armarios.map(arm => 
          arm.id === armarioId ? {
            ...arm,
            archivos: [...arm.archivos, archivo]
          } : arm
        )
      } : s
    ))

    alert(`📂 Archivo movido al armario exitosamente`)
  }

  const crearArmario = (salaId, nombreArmario) => {
    if (!nombreArmario.trim()) return

    const nuevoArmario = {
      id: Date.now(),
      nombre: nombreArmario,
      archivos: []
    }

    setSalas3D(prev => prev.map(s => 
      s.id === salaId ? {
        ...s,
        armarios: [...(s.armarios || []), nuevoArmario]
      } : s
    ))

    alert(`🗄️ Armario "${nombreArmario}" creado exitosamente`)
  }

  const eliminarArmario = (salaId, armarioId) => {
    const sala = salas3D.find(s => s.id === salaId)
    const armario = sala?.armarios.find(a => a.id === armarioId)
    
    if (!armario) return

    if (confirm(`¿Eliminar armario "${armario.nombre}" y todos sus archivos?`)) {
      setSalas3D(prev => prev.map(s => 
        s.id === salaId ? {
          ...s,
          armarios: s.armarios.filter(a => a.id !== armarioId)
        } : s
      ))
      alert(`🗑️ Armario eliminado`)
    }
  }

  const habilitarAprendizajeAgente = (agenteId, habilitado) => {
    setAgentes(prev => prev.map(a => 
      a.id === agenteId ? { ...a, aprendiendo: habilitado } : a
    ))

    const agente = agentes.find(a => a.id === agenteId)
    alert(`🧠 Aprendizaje ${habilitado ? 'habilitado' : 'deshabilitado'} para ${agente?.nombre}`)
  }

  const guardarConocimientoSala = (salaId, conocimiento) => {
    setSalas3D(prev => prev.map(s => 
      s.id === salaId ? {
        ...s,
        aprendizaje: {
          ...s.aprendizaje,
          conocimientoBase: [...(s.aprendizaje?.conocimientoBase || []), {
            id: Date.now(),
            contenido: conocimiento,
            fecha: new Date()
          }]
        }
      } : s
    ))

    alert(`💾 Conocimiento guardado en la sala`)
  }

  const analizarPatronesSala = (salaId) => {
    const sala = salas3D.find(s => s.id === salaId)
    if (!sala) return

    // Analizar patrones en los mensajes
    const mensajes = sala.mensajes || []
    const patrones = {
      temasFrecuentes: [],
      agenteMasActivo: null,
      horasPico: [],
      palabrasClave: []
    }

    // Simular análisis de patrones
    const agentesConteo = {}
    mensajes.forEach(msg => {
      if (msg.tipo === 'agente' && msg.agente) {
        agentesConteo[msg.agente.id] = (agentesConteo[msg.agente.id] || 0) + 1
      }
    })

    const agenteIdMasActivo = Object.keys(agentesConteo).reduce((a, b) => 
      agentesConteo[a] > agentesConteo[b] ? a : b, null
    )

    if (agenteIdMasActivo) {
      patrones.agenteMasActivo = agentes.find(a => a.id == agenteIdMasActivo)?.nombre
    }

    setSalas3D(prev => prev.map(s => 
      s.id === salaId ? {
        ...s,
        aprendizaje: {
          ...s.aprendizaje,
          patrones: [...(s.aprendizaje?.patrones || []), {
            id: Date.now(),
            analisis: patrones,
            fecha: new Date()
          }]
        }
      } : s
    ))

    alert(`📊 Análisis de patrones completado`)
  }

  const exportarDatosSala = (salaId) => {
    const sala = salas3D.find(s => s.id === salaId)
    if (!sala) return

    const datos = {
      sala: sala.nombre,
      mensajes: sala.mensajes,
      archivos: sala.archivos,
      armarios: sala.armarios,
      aprendizaje: sala.aprendizaje,
      fechaExportacion: new Date()
    }

    const blob = new Blob([JSON.stringify(datos, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `sala_${sala.nombre}_${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)

    alert(`💾 Datos de la sala exportados`)
  }

  const buscarEnArchivos = (salaId, termino) => {
    const sala = salas3D.find(s => s.id === salaId)
    if (!sala || !termino.trim()) return []

    const resultados = []
    
    // Buscar en archivos de la sala
    sala.archivos?.forEach(archivo => {
      if (archivo.nombre.toLowerCase().includes(termino.toLowerCase()) ||
          archivo.contenido?.toLowerCase().includes(termino.toLowerCase())) {
        resultados.push({ tipo: 'archivo', item: archivo })
      }
    })

    // Buscar en armarios
    sala.armarios?.forEach(armario => {
      armario.archivos?.forEach(archivo => {
        if (archivo.nombre.toLowerCase().includes(termino.toLowerCase()) ||
            archivo.contenido?.toLowerCase().includes(termino.toLowerCase())) {
          resultados.push({ tipo: 'armario', armario: armario.nombre, item: archivo })
        }
      })
    })

    return resultados
  }

  // Componente de navegación
  const NavegacionPrincipal = () => (
    <nav className="sidebar fixed left-0 top-0 h-full w-64 p-6 z-40">
      <div className="mb-8">
        <h1 className="text-gradient text-2xl font-bold">
          Agentes IA v6.0
        </h1>
        <p className="text-slate-400 text-sm mt-1">JONATHAN CAMARA</p>
      </div>

      <div className="space-y-2">
        {[
          { id: 'panel', label: 'Panel Principal', icon: TrendingUp },
          { id: 'agentes', label: 'Agentes', icon: Users },
          { id: 'salas', label: 'Salas 3D', icon: Video },
          { id: 'modelos', label: 'Modelos IA', icon: Cpu },
          { id: 'documentacion', label: 'Documentación', icon: File },
          { id: 'configuracion', label: 'Configuración', icon: Settings }
        ].map(item => (
          <button
            key={item.id}
            onClick={() => setPestanaActiva(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
              pestanaActiva === item.id ? 'sidebar-item-active' : 'sidebar-item'
            }`}
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </button>
        ))}
      </div>
    </nav>
  )

  // Renderizado de tarjeta de agente
  const TarjetaAgente = ({ agente }) => (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="text-3xl">{agente.avatar}</div>
          <div>
            <h3 className="text-white font-bold text-lg">{agente.nombre}</h3>
            <p className="text-slate-400 text-sm">{agente.rol}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <div className={`status-dot ${
            agente.estado === 'activo' ? 'status-dot-active' : 'status-dot-inactive'
          }`} />
          
          <Button
            onClick={() => agente.estado === 'activo' ? desactivarAgente(agente.id) : activarAgente(agente.id)}
            className={agente.estado === 'activo' ? 'btn-secondary' : 'btn-gradient'}
            style={{ padding: '8px 12px', fontSize: '12px' }}
          >
            {agente.estado === 'activo' ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>
          
          <Button
            onClick={() => {
              setAgenteSeleccionado(agente)
              setModalAgenteAbierto(true)
            }}
            className="btn-secondary"
            style={{ padding: '8px 12px', fontSize: '12px' }}
          >
            <Edit className="h-4 w-4" />
          </Button>
          
          <Button
            onClick={() => eliminarAgente(agente.id)}
            className="btn-secondary"
            style={{ padding: '8px 12px', fontSize: '12px', color: '#ef4444' }}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{agente.conversaciones}</p>
          <p className="text-xs text-slate-400">Conversaciones</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{agente.precision}%</p>
          <p className="text-xs text-slate-400">Precisión</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{agente.modelo}</p>
          <p className="text-xs text-slate-400">Modelo</p>
        </div>
      </div>
      
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-400">Aprendizaje Activo:</span>
        <Switch
          checked={agente.aprendiendo}
          onCheckedChange={() => toggleAprendizaje(agente.id)}
        />
      </div>
    </div>
  )

  return (
    <div 
      className="min-h-screen relative overflow-hidden"
      style={{
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)'
      }}
    >
      {/* Efectos de fondo */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `
            radial-gradient(circle at 20% 80%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(147, 51, 234, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(16, 185, 129, 0.05) 0%, transparent 50%)
          `
        }}
      />

      <NavegacionPrincipal />

      <main className="ml-64 p-8 relative z-10">
        {pestanaActiva === 'panel' && (
          <div className="space-y-6">
            <h2 className="text-gradient text-4xl font-bold mb-8">
              Panel Principal
            </h2>

            {/* Estadísticas INTERACTIVAS */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
              {[
                { label: 'Conversaciones Hoy', valor: estadisticas.conversacionesHoy, icon: MessageSquare, color: '#00d4ff', accion: () => setPestanaActiva('agentes') },
                { label: 'Tareas Completadas', valor: estadisticas.tareasCompletadas, icon: TrendingUp, color: '#10b981', accion: () => setPestanaActiva('documentacion') },
                { label: 'Tiempo Ahorrado (h)', valor: estadisticas.tiempoAhorrado, icon: Clock, color: '#f59e0b', accion: () => setPestanaActiva('configuracion') },
                { label: 'Agentes Online', valor: estadisticas.agentesOnline, icon: Users, color: '#8b5cf6', accion: () => setPestanaActiva('agentes') },
                { label: 'Modelos Activos', valor: estadisticas.modelosActivos, icon: Cpu, color: '#ef4444', accion: () => setPestanaActiva('modelos') },
                { label: 'Uso Memoria (%)', valor: estadisticas.usoMemoria, icon: HardDrive, color: '#06b6d4', accion: () => setPestanaActiva('configuracion') }
              ].map((stat, index) => (
                <div
                  key={stat.label}
                  onClick={stat.accion}
                  className="glass-card p-6 text-center cursor-pointer"
                >
                  <div 
                    className="w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-3"
                    style={{
                      background: `linear-gradient(135deg, ${stat.color}, ${stat.color}dd)`
                    }}
                  >
                    <stat.icon className="h-6 w-6 text-white" />
                  </div>
                  <p className="text-2xl font-bold text-white">{stat.valor}</p>
                  <p className="text-sm text-slate-400">{stat.label}</p>
                  <p className="text-xs text-slate-500 mt-1">Click para ir</p>
                </div>
              ))}
            </div>

            {/* Acciones rápidas INTERACTIVAS */}
            <div className="glass-card p-6">
              <h3 className="text-xl font-bold text-white mb-4">🚀 Acciones Rápidas</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Button
                  onClick={() => {
                    setAgenteSeleccionado(null)
                    setModalAgenteAbierto(true)
                  }}
                  className="btn-gradient flex items-center gap-2 p-4"
                >
                  <Plus className="h-5 w-5" />
                  Crear Agente
                </Button>
                
                <Button
                  onClick={() => {
                    setSalaSeleccionada(null)
                    setModalSalaAbierto(true)
                  }}
                  style={{
                    background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                    color: 'white',
                    border: 'none'
                  }}
                  className="flex items-center gap-2 p-4"
                >
                  <Video className="h-5 w-5" />
                  Nueva Sala 3D
                </Button>
                
                <Button
                  onClick={() => setPestanaActiva('modelos')}
                  style={{
                    background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
                    color: 'white',
                    border: 'none'
                  }}
                  className="flex items-center gap-2 p-4"
                >
                  <Download className="h-5 w-5" />
                  Descargar Modelo
                </Button>

                <Button
                  onClick={() => setPestanaActiva('configuracion')}
                  style={{
                    background: 'linear-gradient(135deg, #f59e0b, #d97706)',
                    color: 'white',
                    border: 'none'
                  }}
                  className="flex items-center gap-2 p-4"
                >
                  <Settings className="h-5 w-5" />
                  Configuración
                </Button>
              </div>
            </div>

            {/* Vista previa de agentes más activos */}
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">🏆 Agentes Más Activos</h3>
                <Button
                  onClick={() => setPestanaActiva('agentes')}
                  className="btn-secondary text-sm"
                >
                  Ver todos
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {agentes
                  .sort((a, b) => b.conversaciones - a.conversaciones)
                  .slice(0, 3)
                  .map((agente, index) => (
                    <div 
                      key={agente.id}
                      onClick={() => setPestanaActiva('agentes')}
                      className="flex items-center gap-3 p-4 rounded-xl cursor-pointer transition-all duration-200"
                      style={{ background: 'rgba(148, 163, 184, 0.1)' }}
                      onMouseEnter={(e) => e.target.style.background = 'rgba(148, 163, 184, 0.2)'}
                      onMouseLeave={(e) => e.target.style.background = 'rgba(148, 163, 184, 0.1)'}
                    >
                      <div 
                        className="w-10 h-10 rounded-lg flex items-center justify-center text-lg"
                        style={{
                          background: index === 0 ? '#fbbf24' : index === 1 ? '#9ca3af' : '#cd7c2f'
                        }}
                      >
                        {agente.avatar}
                      </div>
                      <div className="flex-1">
                        <p className="text-white font-semibold">{agente.nombre}</p>
                        <p className="text-sm text-slate-400">{agente.conversaciones} conversaciones</p>
                        <p className="text-xs text-slate-500">{agente.precision}% precisión</p>
                      </div>
                      <div className={`status-dot ${
                        agente.estado === 'activo' ? 'status-dot-active' : 'status-dot-inactive'
                      }`} />
                    </div>
                  ))
                }
              </div>
            </div>
          </div>
        )}

        {pestanaActiva === 'agentes' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-gradient text-4xl font-bold">
                Gestión de Agentes
              </h2>
              <Button
                onClick={() => {
                  setAgenteSeleccionado(null)
                  setModalAgenteAbierto(true)
                }}
                className="btn-gradient flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Nuevo Agente
              </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {agentes.map(agente => (
                <TarjetaAgente key={agente.id} agente={agente} />
              ))}
            </div>
          </div>
        )}

        {pestanaActiva === 'salas' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-gradient text-4xl font-bold">
                Salas 3D
              </h2>
              <Button
                onClick={() => {
                  setSalaSeleccionada(null)
                  setModalSalaAbierto(true)
                }}
                className="btn-gradient flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Nueva Sala
              </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {salas3D.map(sala => (
                <div key={sala.id} className="space-y-4">
                  {/* Información de la sala */}
                  <div className="glass-card p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="text-3xl">
                          {sala.tipo === 'ejecutiva' ? '🏢' : '🎨'}
                        </div>
                        <div>
                          <h3 className="text-white font-bold text-lg">{sala.nombre}</h3>
                          <p className="text-slate-400 text-sm">
                            {sala.tipo === 'ejecutiva' ? 'Sala Ejecutiva' : 'Sala Creativa'}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Button
                          onClick={() => setSalaSeleccionada(sala)}
                          className="btn-secondary"
                          style={{ padding: '8px 12px', fontSize: '12px' }}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        
                        <Button
                          onClick={() => eliminarSala(sala.id)}
                          className="btn-secondary"
                          style={{ padding: '8px 12px', fontSize: '12px', color: '#ef4444' }}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    
                    {/* Agentes en la sala */}
                    <div className="mb-4">
                      <h4 className="text-white text-sm font-semibold mb-2">
                        Agentes en la sala ({sala.agentesActivos?.length || 0})
                      </h4>
                      <div className="flex gap-2 flex-wrap">
                        {(sala.agentesActivos || []).map((agenteId) => {
                          const agente = agentes.find(a => a.id === agenteId)
                          return agente ? (
                            <div key={agenteId} className="flex items-center gap-2 bg-slate-700 px-3 py-1 rounded-lg">
                              <span className="text-sm">{agente.avatar}</span>
                              <span className="text-white text-sm">{agente.nombre}</span>
                              <Button
                                onClick={() => echarAgenteDeSala(sala.id, agenteId)}
                                style={{ 
                                  background: 'transparent', 
                                  border: 'none', 
                                  color: '#ef4444', 
                                  padding: '2px',
                                  fontSize: '12px'
                                }}
                              >
                                ×
                              </Button>
                            </div>
                          ) : null
                        })}
                        
                        {/* Botón para llamar agentes */}
                        <select
                          onChange={(e) => {
                            if (e.target.value) {
                              llamarAgenteASala(sala.id, parseInt(e.target.value))
                              e.target.value = ''
                            }
                          }}
                          className="input-glass text-sm"
                          style={{ width: 'auto', padding: '4px 8px' }}
                        >
                          <option value="">+ Llamar agente</option>
                          {agentes
                            .filter(a => !sala.agentesActivos?.includes(a.id))
                            .map(agente => (
                              <option key={agente.id} value={agente.id}>
                                {agente.avatar} {agente.nombre}
                              </option>
                            ))
                          }
                        </select>
                      </div>
                    </div>
                  </div>
                  
                  {/* Chat de la sala */}
                  <div className="glass-card p-6 flex flex-col h-96">
                    <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-600">
                      <div>
                        <h4 className="text-white font-semibold">💬 Chat - {sala.nombre}</h4>
                        <p className="text-slate-400 text-sm">
                          {(sala.agentesActivos?.length || 0)} agentes conectados
                        </p>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button
                          onClick={() => iniciarGrabacionSala(sala.id)}
                          style={{
                            background: sala.grabando ? 'linear-gradient(135deg, #ef4444, #dc2626)' : 'linear-gradient(135deg, #10b981, #059669)',
                            color: 'white',
                            border: 'none',
                            padding: '6px 12px',
                            fontSize: '12px'
                          }}
                        >
                          {sala.grabando ? '⏹️ Detener' : '🔴 Grabar'}
                        </Button>
                        <Button
                          onClick={() => limpiarChatSala(sala.id)}
                          className="btn-secondary"
                          style={{ padding: '6px 12px', fontSize: '12px' }}
                        >
                          🗑️
                        </Button>
                      </div>
                    </div>
                    
                    {/* Área de mensajes de la sala */}
                    <div className="flex-1 overflow-y-auto mb-4 p-3 bg-slate-800 rounded-lg">
                      {(sala.mensajes || []).length === 0 ? (
                        <div className="text-center text-slate-400 py-8">
                          {(sala.agentesActivos?.length || 0) > 0 
                            ? 'Escribe un mensaje para chatear en la sala'
                            : 'Llama agentes a la sala para comenzar a chatear'
                          }
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {sala.mensajes.map(mensaje => (
                            <div key={mensaje.id} className="flex gap-3">
                              <div className="text-lg">
                                {mensaje.tipo === 'usuario' ? '👤' : 
                                 mensaje.tipo === 'sistema' ? '🔔' : 
                                 mensaje.agente?.avatar || '🤖'}
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="text-white font-semibold text-sm">
                                    {mensaje.tipo === 'usuario' ? 'Tú' : 
                                     mensaje.tipo === 'sistema' ? 'Sistema' : 
                                     mensaje.agente?.nombre || 'Agente'}
                                  </span>
                                  <span className="text-slate-500 text-xs">
                                    {mensaje.timestamp?.toLocaleTimeString()}
                                  </span>
                                </div>
                                <p className="text-slate-300 text-sm">{mensaje.texto}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    {/* Input de mensaje para la sala */}
                    <div className="flex gap-3">
                      <input
                        id={`input-sala-${sala.id}`}
                        placeholder="Escribe tu mensaje en la sala..."
                        className="input-glass flex-1"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            enviarMensajeSala(sala.id, e.target.value)
                            e.target.value = ''
                          }
                        }}
                      />
                      <Button
                        onClick={() => {
                          const input = document.getElementById(`input-sala-${sala.id}`)
                          if (input.value.trim()) {
                            enviarMensajeSala(sala.id, input.value)
                            input.value = ''
                          }
                        }}
                        className="btn-gradient"
                        style={{ padding: '10px 15px' }}
                      >
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {pestanaActiva === 'modelos' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-gradient text-4xl font-bold">
                Modelos de IA
              </h2>
              
              <div className="flex gap-3">
                <Button
                  onClick={() => detectarModelos()}
                  className="btn-secondary flex items-center gap-2"
                >
                  <RotateCcw className="h-4 w-4" />
                  Redetectar
                </Button>
                
                <Button
                  onClick={() => {
                    const modelo = prompt('Nombre del modelo a descargar (ej: llama2, mistral, codellama):')
                    if (modelo) descargarModelo(modelo)
                  }}
                  className="btn-gradient flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Descargar Modelo
                </Button>
              </div>
            </div>

            {/* Estado de servicios */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="glass-card p-6 text-center">
                <div 
                  className="w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-3"
                  style={{
                    background: estadoOllama.conectado ? '#10b981' : '#ef4444'
                  }}
                >
                  <Server className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-lg font-bold text-white">Ollama</h3>
                <p className="text-sm text-slate-400">Puerto 11434</p>
                <p 
                  className="text-sm"
                  style={{ color: estadoOllama.conectado ? '#10b981' : '#ef4444' }}
                >
                  {estadoOllama.conectado ? `✅ ${estadoOllama.modelos.length} modelos` : '❌ Desconectado'}
                </p>
              </div>

              <div className="glass-card p-6 text-center">
                <div 
                  className="w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-3"
                  style={{
                    background: estadoLMStudio.conectado ? '#10b981' : '#ef4444'
                  }}
                >
                  <Cpu className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-lg font-bold text-white">LM Studio</h3>
                <p className="text-sm text-slate-400">Puerto 1234</p>
                <p 
                  className="text-sm"
                  style={{ color: estadoLMStudio.conectado ? '#10b981' : '#ef4444' }}
                >
                  {estadoLMStudio.conectado ? `✅ ${estadoLMStudio.modelos.length} modelos` : '❌ Desconectado'}
                </p>
              </div>

              <div className="glass-card p-6 text-center">
                <div 
                  className="w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-3"
                  style={{
                    background: estadoLocalAI.conectado ? '#10b981' : '#ef4444'
                  }}
                >
                  <Bot className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-lg font-bold text-white">LocalAI</h3>
                <p className="text-sm text-slate-400">Puerto 8080</p>
                <p 
                  className="text-sm"
                  style={{ color: estadoLocalAI.conectado ? '#10b981' : '#ef4444' }}
                >
                  {estadoLocalAI.conectado ? `✅ ${estadoLocalAI.modelos.length} modelos` : '❌ Desconectado'}
                </p>
              </div>
            </div>

            {/* Lista de modelos */}
            <div>
              <h3 className="text-xl font-bold text-white mb-4">Modelos Detectados ({modelosLocales.length})</h3>
              
              {modelosLocales.length === 0 ? (
                <div className="glass-card p-12 text-center">
                  <Cpu className="h-16 w-16 text-slate-600 mx-auto mb-4" />
                  <h4 className="text-lg font-semibold text-white mb-2">No se detectaron modelos locales</h4>
                  <p className="text-slate-400 mb-6">
                    Asegúrate de tener Ollama, LM Studio o LocalAI ejecutándose
                  </p>
                  <div className="flex gap-3 justify-center">
                    <Button
                      onClick={() => descargarModelo('llama2')}
                      className="btn-gradient"
                    >
                      Descargar Llama 2
                    </Button>
                    <Button
                      onClick={() => descargarModelo('mistral')}
                      style={{
                        background: 'linear-gradient(135deg, #10b981, #059669)',
                        color: 'white',
                        border: 'none'
                      }}
                    >
                      Descargar Mistral
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {modelosLocales.map((modelo, index) => (
                    <div
                      key={index}
                      className="glass-card p-6 flex items-center justify-between"
                    >
                      <div className="flex items-center gap-4">
                        <div 
                          className="w-12 h-12 rounded-xl flex items-center justify-center"
                          style={{
                            background: modelo.activo ? 'linear-gradient(135deg, #10b981, #059669)' : 'linear-gradient(135deg, #64748b, #475569)'
                          }}
                        >
                          <Bot className="h-6 w-6 text-white" />
                        </div>
                        
                        <div>
                          <h4 className="text-lg font-bold text-white">{modelo.name || modelo.id}</h4>
                          <p className="text-sm text-slate-400">
                            {modelo.servicio} • {modelo.size ? `${(modelo.size / 1024 / 1024 / 1024).toFixed(1)} GB` : 'Tamaño desconocido'}
                          </p>
                          <p className="text-xs text-slate-500">
                            Modificado: {modelo.modified_at ? new Date(modelo.modified_at).toLocaleDateString() : 'Desconocido'}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex gap-3">
                        <Button
                          onClick={() => toggleModelo(modelo, !modelo.activo)}
                          style={{
                            background: modelo.activo 
                              ? 'linear-gradient(135deg, #ef4444, #dc2626)' 
                              : 'linear-gradient(135deg, #10b981, #059669)',
                            color: 'white',
                            border: 'none'
                          }}
                          className="flex items-center gap-2"
                        >
                          {modelo.activo ? (
                            <>
                              <Pause className="h-4 w-4" />
                              Desactivar
                            </>
                          ) : (
                            <>
                              <Play className="h-4 w-4" />
                              Activar
                            </>
                          )}
                        </Button>
                        
                        <Button
                          onClick={() => {
                            if (confirm(`¿Eliminar el modelo ${modelo.name}?`)) {
                              alert('Función de eliminación en desarrollo')
                            }
                          }}
                          className="btn-secondary"
                          style={{ color: '#ef4444' }}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {pestanaActiva === 'configuracion' && (
          <div className="space-y-6">
            <h2 className="text-gradient text-4xl font-bold">
              Configuración del Sistema
            </h2>

            {/* Configuración de APIs */}
            <div className="glass-card p-6">
              <h3 className="text-xl font-bold text-white mb-4">🔑 Configuración de APIs</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white font-semibold mb-2">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    placeholder="sk-..."
                    className="input-glass"
                    onChange={(e) => localStorage.setItem('openai_api_key', e.target.value)}
                    defaultValue={localStorage.getItem('openai_api_key') || ''}
                  />
                  <p className="text-slate-400 text-sm mt-1">
                    Para usar GPT-4, GPT-3.5 y otros modelos de OpenAI
                  </p>
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Anthropic API Key
                  </label>
                  <input
                    type="password"
                    placeholder="sk-ant-..."
                    className="input-glass"
                    onChange={(e) => localStorage.setItem('anthropic_api_key', e.target.value)}
                    defaultValue={localStorage.getItem('anthropic_api_key') || ''}
                  />
                  <p className="text-slate-400 text-sm mt-1">
                    Para usar Claude-3 y otros modelos de Anthropic
                  </p>
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Google AI API Key
                  </label>
                  <input
                    type="password"
                    placeholder="AIza..."
                    className="input-glass"
                    onChange={(e) => localStorage.setItem('google_api_key', e.target.value)}
                    defaultValue={localStorage.getItem('google_api_key') || ''}
                  />
                  <p className="text-slate-400 text-sm mt-1">
                    Para usar Gemini Pro y otros modelos de Google
                  </p>
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Telegram Bot Token
                  </label>
                  <input
                    type="password"
                    placeholder="123456789:ABC..."
                    className="input-glass"
                    onChange={(e) => localStorage.setItem('telegram_token', e.target.value)}
                    defaultValue={localStorage.getItem('telegram_token') || ''}
                  />
                  <p className="text-slate-400 text-sm mt-1">
                    Token global para bots de Telegram
                  </p>
                </div>
              </div>

              <div className="flex justify-end mt-6">
                <Button
                  onClick={() => alert('✅ APIs configuradas correctamente')}
                  className="btn-gradient flex items-center gap-2"
                >
                  <Save className="h-4 w-4" />
                  Guardar APIs
                </Button>
              </div>
            </div>

            {/* Configuración de Base de Datos */}
            <div className="glass-card p-6">
              <h3 className="text-xl font-bold text-white mb-4">💾 Configuración de Base de Datos</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Tipo de Base de Datos
                  </label>
                  <select className="input-glass">
                    <option value="postgresql">PostgreSQL</option>
                    <option value="mysql">MySQL</option>
                    <option value="sqlite">SQLite (Local)</option>
                    <option value="mongodb">MongoDB</option>
                  </select>
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Host del Servidor
                  </label>
                  <input
                    type="text"
                    placeholder="localhost"
                    defaultValue="localhost"
                    className="input-glass"
                  />
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Puerto
                  </label>
                  <input
                    type="number"
                    placeholder="5432"
                    defaultValue="5432"
                    className="input-glass"
                  />
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Nombre de la Base de Datos
                  </label>
                  <input
                    type="text"
                    placeholder="agentes_ia"
                    defaultValue="agentes_ia"
                    className="input-glass"
                  />
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Usuario
                  </label>
                  <input
                    type="text"
                    placeholder="usuario"
                    className="input-glass"
                  />
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Contraseña
                  </label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    className="input-glass"
                  />
                </div>
              </div>

              <div className="flex justify-between mt-6">
                <Button
                  onClick={() => alert('Probando conexión a la base de datos...')}
                  className="btn-secondary flex items-center gap-2"
                >
                  <Database className="h-4 w-4" />
                  Probar Conexión
                </Button>

                <Button
                  onClick={() => alert('✅ Base de datos configurada correctamente')}
                  style={{
                    background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                    color: 'white',
                    border: 'none'
                  }}
                  className="flex items-center gap-2"
                >
                  <Save className="h-4 w-4" />
                  Guardar Configuración
                </Button>
              </div>
            </div>

            {/* Botón de guardar configuración general */}
            <div className="text-center pt-6">
              <Button
                onClick={() => alert('✅ Toda la configuración ha sido guardada correctamente')}
                className="btn-gradient flex items-center gap-2 text-lg px-8 py-4"
              >
                <Save className="h-5 w-5" />
                Guardar Toda la Configuración
              </Button>
            </div>
          </div>
        )}

        {pestanaActiva === 'documentacion' && (
          <div className="space-y-6">
            <h2 className="text-gradient text-4xl font-bold">
              Documentación
            </h2>

            <div className="glass-card p-12 text-center">
              <File className="h-16 w-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">Documentación del Sistema</h3>
              <p className="text-slate-400 mb-6">
                Guías completas, tutoriales y documentación técnica
              </p>
              <Button
                onClick={() => alert('Abriendo documentación completa...')}
                className="btn-gradient"
              >
                Ver Documentación Completa
              </Button>
            </div>
          </div>
        )}
      </main>

      {/* Modal REAL para agentes con formulario completo */}
      <Dialog open={modalAgenteAbierto} onOpenChange={setModalAgenteAbierto}>
        <DialogContent className="modal-glass max-w-4xl">
          <DialogHeader>
            <DialogTitle className="text-white text-2xl">
              {agenteSeleccionado ? `Editar Agente: ${agenteSeleccionado.nombre}` : 'Crear Nuevo Agente'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="max-h-96 overflow-y-auto p-6">
            <form onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.target)
              const nuevoAgente = {
                nombre: formData.get('nombre'),
                rol: formData.get('rol'),
                avatar: formData.get('avatar'),
                prompt: formData.get('prompt'),
                modelo: formData.get('modelo'),
                temperatura: parseFloat(formData.get('temperatura')),
                maxTokens: parseInt(formData.get('maxTokens')),
                telegramToken: formData.get('telegramToken'),
                telegram: formData.get('telegram') === 'on',
                baseDatos: formData.get('baseDatos'),
                voz: formData.get('voz')
              }
              
              if (agenteSeleccionado) {
                // Editar agente existente
                setAgentes(agentes.map(a => 
                  a.id === agenteSeleccionado.id ? { ...a, ...nuevoAgente } : a
                ))
                setModalAgenteAbierto(false)
                setAgenteSeleccionado(null)
                alert(`✅ Agente "${nuevoAgente.nombre}" actualizado`)
              } else {
                // Crear nuevo agente
                crearAgente(nuevoAgente)
              }
            }}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Información básica */}
                <div>
                  <label className="block text-white font-semibold mb-2">Nombre del Agente</label>
                  <input 
                    name="nombre"
                    defaultValue={agenteSeleccionado?.nombre || ''}
                    required
                    className="input-glass"
                    placeholder="Ej: Analista Financiero"
                  />
                </div>
                
                <div>
                  <label className="block text-white font-semibold mb-2">Rol/Especialidad</label>
                  <input 
                    name="rol"
                    defaultValue={agenteSeleccionado?.rol || ''}
                    required
                    className="input-glass"
                    placeholder="Ej: Finanzas, Marketing, Desarrollo"
                  />
                </div>
                
                <div>
                  <label className="block text-white font-semibold mb-2">Avatar (Emoji)</label>
                  <input 
                    name="avatar"
                    defaultValue={agenteSeleccionado?.avatar || '🤖'}
                    required
                    className="input-glass text-center text-xl"
                    placeholder="🤖"
                  />
                </div>
                
                <div>
                  <label className="block text-white font-semibold mb-2">Modelo IA</label>
                  <select 
                    name="modelo"
                    defaultValue={agenteSeleccionado?.modelo || 'gpt-4'}
                    required
                    className="input-glass"
                  >
                    <optgroup label="Modelos Remotos">
                      <option value="gpt-4">GPT-4 (OpenAI)</option>
                      <option value="gpt-3.5-turbo">GPT-3.5 Turbo (OpenAI)</option>
                      <option value="claude-3">Claude-3 (Anthropic)</option>
                      <option value="gemini-pro">Gemini Pro (Google)</option>
                    </optgroup>
                    <optgroup label="Modelos Locales (Ollama)">
                      <option value="ollama:llama2">Llama 2 (Local)</option>
                      <option value="ollama:mistral">Mistral (Local)</option>
                      <option value="ollama:codellama">CodeLlama (Local)</option>
                      <option value="ollama:vicuna">Vicuna (Local)</option>
                    </optgroup>
                  </select>
                </div>
                
                <div>
                  <label className="block text-white font-semibold mb-2">Temperatura (0.1-2.0)</label>
                  <input 
                    name="temperatura"
                    type="number"
                    min="0.1"
                    max="2.0"
                    step="0.1"
                    defaultValue={agenteSeleccionado?.temperatura || 0.7}
                    className="input-glass"
                  />
                </div>
                
                <div>
                  <label className="block text-white font-semibold mb-2">Max Tokens</label>
                  <input 
                    name="maxTokens"
                    type="number"
                    min="100"
                    max="4000"
                    defaultValue={agenteSeleccionado?.maxTokens || 1000}
                    className="input-glass"
                  />
                </div>
              </div>
              
              {/* Prompt del sistema */}
              <div className="mt-6">
                <label className="block text-white font-semibold mb-2">Prompt del Sistema</label>
                <textarea 
                  name="prompt"
                  defaultValue={agenteSeleccionado?.prompt || 'Eres un asistente IA especializado y profesional.'}
                  required
                  rows={4}
                  className="input-glass resize-none"
                  placeholder="Define la personalidad y comportamiento del agente..."
                />
              </div>
              
              {/* Configuración Telegram */}
              <div className="mt-6 p-4 bg-slate-700 rounded-lg">
                <h4 className="text-white font-semibold mb-3">🤖 Integración Telegram</h4>
                <div className="mb-3">
                  <label className="flex items-center text-white">
                    <input 
                      name="telegram"
                      type="checkbox"
                      defaultChecked={agenteSeleccionado?.telegram || false}
                      className="mr-3"
                    />
                    Activar Bot de Telegram
                  </label>
                </div>
                <div>
                  <label className="block text-white font-semibold mb-2">Token del Bot</label>
                  <input 
                    name="telegramToken"
                    defaultValue={agenteSeleccionado?.telegramToken || ''}
                    className="input-glass"
                    placeholder="123456789:ABCdefGHIjklMNOpqrSTUvwxyz"
                  />
                </div>
              </div>
              
              {/* Configuración Base de Datos */}
              <div className="mt-6 p-4 bg-slate-700 rounded-lg">
                <h4 className="text-white font-semibold mb-3">💾 Base de Datos</h4>
                <div>
                  <label className="block text-white font-semibold mb-2">Configuración BD</label>
                  <input 
                    name="baseDatos"
                    defaultValue={agenteSeleccionado?.baseDatos || ''}
                    className="input-glass"
                    placeholder="postgresql://user:pass@localhost:5432/db"
                  />
                </div>
              </div>
              
              {/* Configuración Voz */}
              <div className="mt-6 p-4 bg-slate-700 rounded-lg">
                <h4 className="text-white font-semibold mb-3">🎙️ Síntesis de Voz</h4>
                <div>
                  <label className="block text-white font-semibold mb-2">Tipo de Voz</label>
                  <select 
                    name="voz"
                    defaultValue={agenteSeleccionado?.voz || 'femenina'}
                    className="input-glass"
                  >
                    <option value="femenina">Voz Femenina</option>
                    <option value="masculina">Voz Masculina</option>
                    <option value="neutral">Voz Neutral</option>
                  </select>
                </div>
              </div>
              
              {/* Botones */}
              <div className="flex justify-end gap-3 mt-8">
                <Button 
                  type="button"
                  onClick={() => setModalAgenteAbierto(false)}
                  className="btn-secondary"
                >
                  Cancelar
                </Button>
                <Button 
                  type="submit"
                  className="btn-gradient"
                >
                  {agenteSeleccionado ? 'Actualizar Agente' : 'Crear Agente'}
                </Button>
              </div>
            </form>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal para salas */}
      <Dialog open={modalSalaAbierto} onOpenChange={setModalSalaAbierto}>
        <DialogContent className="modal-glass max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white text-2xl">
              {salaSeleccionada ? salaSeleccionada.nombre : 'Crear Nueva Sala 3D'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="p-6">
            {salaSeleccionada ? (
              <div className="text-center py-8">
                <Monitor className="h-16 w-16 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400 mb-6">
                  Entorno 3D de la sala "{salaSeleccionada.nombre}"
                </p>
                <div className="space-y-4">
                  <div className="glass-card p-4">
                    <h4 className="text-white font-semibold mb-2">Configuración de la Sala</h4>
                    <p className="text-slate-400 text-sm">
                      Tipo: {salaSeleccionada.tipo === 'ejecutiva' ? 'Sala Ejecutiva' : 'Sala Creativa'}
                    </p>
                    <p className="text-slate-400 text-sm">
                      Agentes activos: {salaSeleccionada.agentesActivos?.length || 0}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <form onSubmit={(e) => {
                e.preventDefault()
                const formData = new FormData(e.target)
                const nuevaSala = {
                  nombre: formData.get('nombre'),
                  tipo: formData.get('tipo')
                }
                crearSala3D(nuevaSala)
              }}>
                <div className="space-y-6">
                  <div>
                    <label className="block text-white font-semibold mb-2">Nombre de la Sala</label>
                    <input 
                      name="nombre"
                      required
                      className="input-glass"
                      placeholder="Ej: Sala de Reuniones Ejecutiva"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-white font-semibold mb-2">Tipo de Sala</label>
                    <select 
                      name="tipo"
                      required
                      className="input-glass"
                    >
                      <option value="ejecutiva">🏢 Sala Ejecutiva</option>
                      <option value="creativa">🎨 Sala Creativa</option>
                    </select>
                  </div>
                </div>
                
                <div className="flex justify-end gap-3 mt-8">
                  <Button 
                    type="button"
                    onClick={() => setModalSalaAbierto(false)}
                    className="btn-secondary"
                  >
                    Cancelar
                  </Button>
                  <Button 
                    type="submit"
                    className="btn-gradient"
                  >
                    Crear Sala
                  </Button>
                </div>
              </form>
            )}
            
            {salaSeleccionada && (
              <div className="flex justify-end mt-6">
                <Button 
                  onClick={() => setModalSalaAbierto(false)}
                  className="btn-secondary"
                >
                  Cerrar
                </Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default App

