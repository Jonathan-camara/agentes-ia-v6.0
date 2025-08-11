import React, { useState, useEffect, useRef } from 'react'
import './App.css'
import { 
  MessageSquare, TrendingUp, Clock, Users, Cpu, HardDrive, 
  Plus, Settings, Video, Download, Save, Database, User, 
  Edit, Upload, File, Trash2, Play, Pause, RotateCcw, 
  Server, Bot, Monitor, Send, Mic, MicOff, Volume2, VolumeX,
  Eye, EyeOff, Shield, Key, Globe, Wifi, WifiOff, Search,
  FileText, Image, Archive, Folder, FolderOpen, Cloud,
  Brain, BookOpen, Zap, CheckCircle, AlertCircle
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

// Clase para conexiones REALES usando el backend
class ConexionesReales {
  static async verificarOllama() {
    try {
      const response = await fetch('/api/modelos/detectar')
      if (response.ok) {
        const data = await response.json()
        const ollama = data.ollama || { conectado: false, modelos: [] }
        console.log('✅ Ollama detectado:', ollama)
        return ollama
      }
    } catch (error) {
      console.log('❌ Error verificando Ollama:', error.message)
    }
    return { conectado: false, modelos: [] }
  }

  static async verificarLMStudio() {
    try {
      const response = await fetch('/api/modelos/detectar')
      if (response.ok) {
        const data = await response.json()
        const lmstudio = data.lmstudio || { conectado: false, modelos: [] }
        console.log('✅ LM Studio detectado:', lmstudio)
        return lmstudio
      }
    } catch (error) {
      console.log('❌ Error verificando LM Studio:', error.message)
    }
    return { conectado: false, modelos: [] }
  }

  static async verificarLocalAI() {
    try {
      const response = await fetch('/api/modelos/detectar')
      if (response.ok) {
        const data = await response.json()
        const localai = data.localai || { conectado: false, modelos: [] }
        console.log('✅ LocalAI detectado:', localai)
        return localai
      }
    } catch (error) {
      console.log('❌ Error verificando LocalAI:', error.message)
    }
    return { conectado: false, modelos: [] }
  }

  static async generarRespuesta(mensaje, agente) {
    try {
      // Usar el backend para generar respuestas
      const response = await fetch('/api/modelos/generar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          modelo: agente.modelo,
          mensaje: mensaje,
          prompt_sistema: agente.prompt || 'Eres un asistente útil.',
          temperatura: agente.temperatura || 0.7,
          max_tokens: agente.maxTokens || 1000,
          busqueda_web: agente.busquedaWeb || false,
          acceso_archivos: agente.accesoArchivos || false,
          acceso_armario: agente.accesoArmario || false
        })
      })

      if (response.ok) {
        const data = await response.json()
        return data.respuesta || 'Sin respuesta'
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Error del servidor')
      }
    } catch (error) {
      console.error('Error generando respuesta:', error)
      return `Error: ${error.message}`
    }
  }

  static async buscarWeb(consulta) {
    try {
      const response = await fetch('/api/web/buscar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ consulta, num_resultados: 5 })
      })

      if (response.ok) {
        const data = await response.json()
        return data.resultados || []
      }
    } catch (error) {
      console.error('Error en búsqueda web:', error)
    }
    return []
  }

  static async subirArchivo(archivo, destino = 'general', agenteId = null) {
    try {
      const formData = new FormData()
      formData.append('archivo', archivo)
      formData.append('destino', destino)
      if (agenteId) formData.append('agente_id', agenteId)

      const response = await fetch('/api/archivos/subir', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        return data
      }
    } catch (error) {
      console.error('Error subiendo archivo:', error)
    }
    return null
  }

  static async listarArchivos(destino = 'general') {
    try {
      const response = await fetch(`/api/archivos/listar?destino=${destino}`)
      if (response.ok) {
        const data = await response.json()
        return data.archivos || []
      }
    } catch (error) {
      console.error('Error listando archivos:', error)
    }
    return []
  }

  static async eliminarArchivo(archivoId) {
    try {
      const response = await fetch(`/api/archivos/eliminar/${archivoId}`, {
        method: 'DELETE'
      })
      return response.ok
    } catch (error) {
      console.error('Error eliminando archivo:', error)
      return false
    }
  }
}

// Componente principal
function App() {
  // Estados para nuevas funcionalidades
  const [archivosSubidos, setArchivosSubidos] = useState([])
  const [armarioDocumentos, setArmarioDocumentos] = useState([])
  const [busquedaWeb, setBusquedaWeb] = useState('')
  const [resultadosBusqueda, setResultadosBusqueda] = useState([])
  const [archivoSeleccionado, setArchivoSeleccionado] = useState(null)
  const [pestanaActiva, setPestanaActiva] = useState('panel')
  const [modalSubirArchivo, setModalSubirArchivo] = useState(false)
  const [modalBusquedaWeb, setModalBusquedaWeb] = useState(false)
  const [modalArmario, setModalArmario] = useState(false)
  const [cargandoBusqueda, setCargandoBusqueda] = useState(false)
  const [cargandoArchivo, setCargandoArchivo] = useState(false)

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
      busquedaWeb: false,
      accesoArchivos: false,
      accesoArmario: false,
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
      busquedaWeb: true,
      accesoArchivos: true,
      accesoArmario: false,
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
      busquedaWeb: true,
      accesoArchivos: false,
      accesoArmario: true,
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
      busquedaWeb: false,
      accesoArchivos: true,
      accesoArmario: false,
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

  // Referencias para archivos
  const inputArchivoRef = useRef(null)
  const inputArmarioRef = useRef(null)

  // Efectos
  useEffect(() => {
    detectarModelos()
    cargarArchivosSubidos()
    cargarArmarioDocumentos()
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

  // Funciones para archivos
  const cargarArchivosSubidos = async () => {
    try {
      const archivos = await ConexionesReales.listarArchivos('general')
      setArchivosSubidos(archivos)
    } catch (error) {
      console.error('Error cargando archivos:', error)
    }
  }

  const cargarArmarioDocumentos = async () => {
    try {
      const archivos = await ConexionesReales.listarArchivos('armario')
      setArmarioDocumentos(archivos)
    } catch (error) {
      console.error('Error cargando armario:', error)
    }
  }

  const manejarSubidaArchivo = async (evento) => {
    const archivo = evento.target.files[0]
    if (!archivo) return

    setCargandoArchivo(true)
    try {
      const resultado = await ConexionesReales.subirArchivo(archivo, 'general')
      if (resultado) {
        await cargarArchivosSubidos()
        alert(`✅ Archivo "${archivo.name}" subido exitosamente`)
        setModalSubirArchivo(false)
      } else {
        alert('❌ Error subiendo archivo')
      }
    } catch (error) {
      console.error('Error:', error)
      alert('❌ Error subiendo archivo')
    } finally {
      setCargandoArchivo(false)
      if (inputArchivoRef.current) {
        inputArchivoRef.current.value = ''
      }
    }
  }

  const manejarSubidaArmario = async (evento) => {
    const archivo = evento.target.files[0]
    if (!archivo) return

    setCargandoArchivo(true)
    try {
      const resultado = await ConexionesReales.subirArchivo(archivo, 'armario')
      if (resultado) {
        await cargarArmarioDocumentos()
        alert(`✅ Documento "${archivo.name}" agregado al armario`)
        setModalArmario(false)
      } else {
        alert('❌ Error subiendo documento al armario')
      }
    } catch (error) {
      console.error('Error:', error)
      alert('❌ Error subiendo documento al armario')
    } finally {
      setCargandoArchivo(false)
      if (inputArmarioRef.current) {
        inputArmarioRef.current.value = ''
      }
    }
  }

  const eliminarArchivo = async (archivoId) => {
    if (!confirm('¿Eliminar este archivo?')) return

    try {
      const exito = await ConexionesReales.eliminarArchivo(archivoId)
      if (exito) {
        await cargarArchivosSubidos()
        await cargarArmarioDocumentos()
        alert('🗑️ Archivo eliminado exitosamente')
      } else {
        alert('❌ Error eliminando archivo')
      }
    } catch (error) {
      console.error('Error:', error)
      alert('❌ Error eliminando archivo')
    }
  }

  // Funciones para búsqueda web
  const realizarBusquedaWeb = async () => {
    if (!busquedaWeb.trim()) return

    setCargandoBusqueda(true)
    try {
      const resultados = await ConexionesReales.buscarWeb(busquedaWeb)
      setResultadosBusqueda(resultados)
      alert(`🔍 Encontrados ${resultados.length} resultados`)
    } catch (error) {
      console.error('Error en búsqueda:', error)
      alert('❌ Error en búsqueda web')
    } finally {
      setCargandoBusqueda(false)
    }
  }

  // Funciones para agentes
  const toggleBusquedaWeb = (agenteId) => {
    setAgentes(prev => prev.map(a => 
      a.id === agenteId ? { ...a, busquedaWeb: !a.busquedaWeb } : a
    ))
  }

  const toggleAccesoArchivos = (agenteId) => {
    setAgentes(prev => prev.map(a => 
      a.id === agenteId ? { ...a, accesoArchivos: !a.accesoArchivos } : a
    ))
  }

  const toggleAccesoArmario = (agenteId) => {
    setAgentes(prev => prev.map(a => 
      a.id === agenteId ? { ...a, accesoArmario: !a.accesoArmario } : a
    ))
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

    alert(`⏸️ Agente "${agente.nombre}" desactivado`)
  }

  const obtenerIconoArchivo = (tipo) => {
    if (tipo.includes('pdf')) return '📄'
    if (tipo.includes('word') || tipo.includes('document')) return '📝'
    if (tipo.includes('excel') || tipo.includes('spreadsheet')) return '📊'
    if (tipo.includes('image')) return '🖼️'
    if (tipo.includes('text')) return '📃'
    return '📁'
  }

  const formatearTamaño = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // Render del componente principal
  return (
    <div className="app-container">
      {/* Header */}
      <header className="header-glass">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="logo-container">
              <Bot className="w-8 h-8 text-blue-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">
                Agentes Virtuales Inteligentes de JONATHAN CAMARA v6.0
              </h1>
              <p className="text-blue-200 text-sm">Sistema completo con funcionalidades REALES</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="status-indicator">
              <div className={`w-3 h-3 rounded-full ${estadoOllama.conectado ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-sm text-white">Ollama</span>
            </div>
            <div className="status-indicator">
              <div className={`w-3 h-3 rounded-full ${estadoLMStudio.conectado ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-sm text-white">LM Studio</span>
            </div>
            <div className="status-indicator">
              <div className={`w-3 h-3 rounded-full ${estadoLocalAI.conectado ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-sm text-white">LocalAI</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="nav-glass">
        <div className="flex space-x-1">
          {[
            { id: 'panel', label: 'Panel Principal', icon: Monitor },
            { id: 'agentes', label: 'Agentes IA', icon: Bot },
            { id: 'salas', label: 'Salas 3D', icon: Video },
            { id: 'modelos', label: 'Modelos IA', icon: Cpu },
            { id: 'archivos', label: 'Gestión de Archivos', icon: FileText },
            { id: 'busqueda', label: 'Búsqueda Web', icon: Search },
            { id: 'armario', label: 'Armario de Documentos', icon: Archive }
          ].map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setPestanaActiva(tab.id)}
                className={`nav-tab ${pestanaActiva === tab.id ? 'nav-tab-active' : ''}`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {/* Panel Principal */}
        {pestanaActiva === 'panel' && (
          <div className="space-y-6">
            {/* Estadísticas */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
              {[
                { label: 'Conversaciones Hoy', value: estadisticas.conversacionesHoy, icon: MessageSquare, color: 'text-blue-400' },
                { label: 'Tareas Completadas', value: estadisticas.tareasCompletadas, icon: CheckCircle, color: 'text-green-400' },
                { label: 'Tiempo Ahorrado (h)', value: estadisticas.tiempoAhorrado, icon: Clock, color: 'text-purple-400' },
                { label: 'Agentes Online', value: estadisticas.agentesOnline, icon: Users, color: 'text-orange-400' },
                { label: 'Modelos Activos', value: estadisticas.modelosActivos, icon: Cpu, color: 'text-cyan-400' },
                { label: 'Uso Memoria (%)', value: estadisticas.usoMemoria, icon: HardDrive, color: 'text-red-400' }
              ].map((stat, index) => {
                const Icon = stat.icon
                return (
                  <div key={index} className="stat-card">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-400 text-sm">{stat.label}</p>
                        <p className="text-2xl font-bold text-white">{stat.value}</p>
                      </div>
                      <Icon className={`w-8 h-8 ${stat.color}`} />
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Resumen de Agentes */}
            <div className="card-glass">
              <h3 className="text-xl font-bold text-white mb-4">🤖 Agentes Activos</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {agentes.map(agente => (
                  <div key={agente.id} className="agent-summary-card">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{agente.avatar}</span>
                      <div className="flex-1">
                        <h4 className="font-semibold text-white">{agente.nombre}</h4>
                        <p className="text-sm text-gray-400">{agente.rol}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <div className={`w-2 h-2 rounded-full ${agente.estado === 'activo' ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                          <span className="text-xs text-gray-400">{agente.estado}</span>
                        </div>
                      </div>
                    </div>
                    <div className="mt-3 flex items-center justify-between text-xs text-gray-400">
                      <span>💬 {agente.conversaciones}</span>
                      <span>🎯 {agente.precision}%</span>
                    </div>
                    <div className="mt-2 flex items-center space-x-1">
                      {agente.busquedaWeb && <Globe className="w-3 h-3 text-blue-400" title="Búsqueda Web" />}
                      {agente.accesoArchivos && <FileText className="w-3 h-3 text-green-400" title="Acceso a Archivos" />}
                      {agente.accesoArmario && <Archive className="w-3 h-3 text-purple-400" title="Acceso al Armario" />}
                      {agente.aprendiendo && <Brain className="w-3 h-3 text-orange-400" title="Aprendizaje Activo" />}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Estado de Servicios */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="card-glass">
                <h4 className="font-semibold text-white mb-3">🦙 Ollama</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Estado:</span>
                    <span className={estadoOllama.conectado ? 'text-green-400' : 'text-red-400'}>
                      {estadoOllama.conectado ? 'Conectado' : 'Desconectado'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Modelos:</span>
                    <span className="text-white">{estadoOllama.modelos.length}</span>
                  </div>
                </div>
              </div>

              <div className="card-glass">
                <h4 className="font-semibold text-white mb-3">🏠 LM Studio</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Estado:</span>
                    <span className={estadoLMStudio.conectado ? 'text-green-400' : 'text-red-400'}>
                      {estadoLMStudio.conectado ? 'Conectado' : 'Desconectado'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Modelos:</span>
                    <span className="text-white">{estadoLMStudio.modelos.length}</span>
                  </div>
                </div>
              </div>

              <div className="card-glass">
                <h4 className="font-semibold text-white mb-3">🤖 LocalAI</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Estado:</span>
                    <span className={estadoLocalAI.conectado ? 'text-green-400' : 'text-red-400'}>
                      {estadoLocalAI.conectado ? 'Conectado' : 'Desconectado'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Modelos:</span>
                    <span className="text-white">{estadoLocalAI.modelos.length}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Gestión de Archivos */}
        {pestanaActiva === 'archivos' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">📁 Gestión de Archivos</h2>
              <Button
                onClick={() => setModalSubirArchivo(true)}
                className="btn-primary"
              >
                <Upload className="w-4 h-4 mr-2" />
                Subir Archivo
              </Button>
            </div>

            <div className="card-glass">
              <h3 className="text-xl font-semibold text-white mb-4">📂 Archivos Subidos</h3>
              {archivosSubidos.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-400">No hay archivos subidos</p>
                  <p className="text-sm text-gray-500 mt-2">Los agentes podrán acceder a los archivos que subas aquí</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {archivosSubidos.map(archivo => (
                    <div key={archivo.id} className="file-card">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">{obtenerIconoArchivo(archivo.tipo)}</span>
                          <div className="flex-1">
                            <h4 className="font-semibold text-white text-sm">{archivo.nombre}</h4>
                            <p className="text-xs text-gray-400">{formatearTamaño(archivo.tamaño)}</p>
                            <p className="text-xs text-gray-500">{new Date(archivo.fecha_subida).toLocaleDateString()}</p>
                          </div>
                        </div>
                        <Button
                          onClick={() => eliminarArchivo(archivo.id)}
                          className="btn-danger-sm"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                      {archivo.contenido_extraido && (
                        <div className="mt-3 p-2 bg-gray-800 rounded text-xs text-gray-300">
                          <p className="font-semibold mb-1">Contenido extraído:</p>
                          <p className="truncate">{archivo.contenido_extraido.substring(0, 100)}...</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="card-glass">
              <h3 className="text-xl font-semibold text-white mb-4">⚙️ Configuración de Acceso</h3>
              <div className="space-y-4">
                {agentes.map(agente => (
                  <div key={agente.id} className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-xl">{agente.avatar}</span>
                      <div>
                        <h4 className="font-semibold text-white">{agente.nombre}</h4>
                        <p className="text-sm text-gray-400">{agente.rol}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-400">Acceso a Archivos</span>
                        <Switch
                          checked={agente.accesoArchivos}
                          onCheckedChange={() => toggleAccesoArchivos(agente.id)}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Búsqueda Web */}
        {pestanaActiva === 'busqueda' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">🔍 Búsqueda Web</h2>
              <Button
                onClick={() => setModalBusquedaWeb(true)}
                className="btn-primary"
              >
                <Search className="w-4 h-4 mr-2" />
                Nueva Búsqueda
              </Button>
            </div>

            <div className="card-glass">
              <h3 className="text-xl font-semibold text-white mb-4">🌐 Búsqueda en Internet</h3>
              <div className="flex space-x-4 mb-6">
                <input
                  type="text"
                  value={busquedaWeb}
                  onChange={(e) => setBusquedaWeb(e.target.value)}
                  placeholder="Escribe tu consulta de búsqueda..."
                  className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  onKeyPress={(e) => e.key === 'Enter' && realizarBusquedaWeb()}
                />
                <Button
                  onClick={realizarBusquedaWeb}
                  disabled={cargandoBusqueda || !busquedaWeb.trim()}
                  className="btn-primary"
                >
                  {cargandoBusqueda ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Search className="w-4 h-4" />
                  )}
                  {cargandoBusqueda ? 'Buscando...' : 'Buscar'}
                </Button>
              </div>

              {resultadosBusqueda.length > 0 && (
                <div className="space-y-4">
                  <h4 className="font-semibold text-white">📋 Resultados de Búsqueda</h4>
                  {resultadosBusqueda.map((resultado, index) => (
                    <div key={index} className="search-result-card">
                      <h5 className="font-semibold text-blue-400 mb-2">{resultado.titulo}</h5>
                      <p className="text-gray-300 text-sm mb-2">{resultado.descripcion}</p>
                      <a
                        href={resultado.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 text-sm hover:underline"
                      >
                        {resultado.url}
                      </a>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="card-glass">
              <h3 className="text-xl font-semibold text-white mb-4">⚙️ Configuración de Búsqueda Web</h3>
              <div className="space-y-4">
                {agentes.map(agente => (
                  <div key={agente.id} className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-xl">{agente.avatar}</span>
                      <div>
                        <h4 className="font-semibold text-white">{agente.nombre}</h4>
                        <p className="text-sm text-gray-400">{agente.rol}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <Globe className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-400">Búsqueda Web</span>
                        <Switch
                          checked={agente.busquedaWeb}
                          onCheckedChange={() => toggleBusquedaWeb(agente.id)}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Armario de Documentos */}
        {pestanaActiva === 'armario' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">🗄️ Armario de Documentos</h2>
              <Button
                onClick={() => setModalArmario(true)}
                className="btn-primary"
              >
                <Archive className="w-4 h-4 mr-2" />
                Agregar Documento
              </Button>
            </div>

            <div className="card-glass">
              <h3 className="text-xl font-semibold text-white mb-4">📚 Documentos del Armario</h3>
              <p className="text-gray-400 mb-4">
                Los documentos del armario están disponibles para todos los agentes en las salas de reuniones
              </p>
              
              {armarioDocumentos.length === 0 ? (
                <div className="text-center py-8">
                  <Archive className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-400">No hay documentos en el armario</p>
                  <p className="text-sm text-gray-500 mt-2">Los agentes podrán consultar los documentos que agregues aquí durante las reuniones</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {armarioDocumentos.map(documento => (
                    <div key={documento.id} className="file-card">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">{obtenerIconoArchivo(documento.tipo)}</span>
                          <div className="flex-1">
                            <h4 className="font-semibold text-white text-sm">{documento.nombre}</h4>
                            <p className="text-xs text-gray-400">{formatearTamaño(documento.tamaño)}</p>
                            <p className="text-xs text-gray-500">{new Date(documento.fecha_subida).toLocaleDateString()}</p>
                          </div>
                        </div>
                        <Button
                          onClick={() => eliminarArchivo(documento.id)}
                          className="btn-danger-sm"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                      {documento.contenido_extraido && (
                        <div className="mt-3 p-2 bg-gray-800 rounded text-xs text-gray-300">
                          <p className="font-semibold mb-1">Contenido extraído:</p>
                          <p className="truncate">{documento.contenido_extraido.substring(0, 100)}...</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="card-glass">
              <h3 className="text-xl font-semibold text-white mb-4">⚙️ Configuración de Acceso al Armario</h3>
              <div className="space-y-4">
                {agentes.map(agente => (
                  <div key={agente.id} className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-xl">{agente.avatar}</span>
                      <div>
                        <h4 className="font-semibold text-white">{agente.nombre}</h4>
                        <p className="text-sm text-gray-400">{agente.rol}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <Archive className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-400">Acceso al Armario</span>
                        <Switch
                          checked={agente.accesoArmario}
                          onCheckedChange={() => toggleAccesoArmario(agente.id)}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Agentes IA */}
        {pestanaActiva === 'agentes' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">🤖 Agentes IA</h2>
              <Button
                onClick={() => {
                  setAgenteSeleccionado(null)
                  setModalAgenteAbierto(true)
                }}
                className="btn-primary"
              >
                <Plus className="w-4 h-4 mr-2" />
                Crear Agente
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {agentes.map(agente => (
                <div key={agente.id} className="agent-card">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <span className="text-3xl">{agente.avatar}</span>
                      <div>
                        <h3 className="font-bold text-white">{agente.nombre}</h3>
                        <p className="text-sm text-gray-400">{agente.rol}</p>
                      </div>
                    </div>
                    <div className={`status-badge ${agente.estado === 'activo' ? 'status-active' : 'status-inactive'}`}>
                      {agente.estado}
                    </div>
                  </div>

                  <div className="space-y-3 mb-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Modelo:</span>
                      <span className="text-white">{agente.modelo}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Conversaciones:</span>
                      <span className="text-white">{agente.conversaciones}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Precisión:</span>
                      <span className="text-white">{agente.precision}%</span>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Brain className="w-4 h-4 text-orange-400" />
                        <span className="text-sm text-gray-400">Aprendizaje</span>
                      </div>
                      <Switch
                        checked={agente.aprendiendo}
                        onCheckedChange={() => toggleAprendizaje(agente.id)}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Globe className="w-4 h-4 text-blue-400" />
                        <span className="text-sm text-gray-400">Búsqueda Web</span>
                      </div>
                      <Switch
                        checked={agente.busquedaWeb}
                        onCheckedChange={() => toggleBusquedaWeb(agente.id)}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-green-400" />
                        <span className="text-sm text-gray-400">Acceso Archivos</span>
                      </div>
                      <Switch
                        checked={agente.accesoArchivos}
                        onCheckedChange={() => toggleAccesoArchivos(agente.id)}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Archive className="w-4 h-4 text-purple-400" />
                        <span className="text-sm text-gray-400">Acceso Armario</span>
                      </div>
                      <Switch
                        checked={agente.accesoArmario}
                        onCheckedChange={() => toggleAccesoArmario(agente.id)}
                      />
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    {agente.estado === 'inactivo' ? (
                      <Button
                        onClick={() => activarAgente(agente.id)}
                        className="btn-success flex-1"
                      >
                        <Play className="w-4 h-4 mr-2" />
                        Activar
                      </Button>
                    ) : (
                      <Button
                        onClick={() => desactivarAgente(agente.id)}
                        className="btn-warning flex-1"
                      >
                        <Pause className="w-4 h-4 mr-2" />
                        Desactivar
                      </Button>
                    )}
                    <Button
                      onClick={() => {
                        setAgenteSeleccionado(agente)
                        setModalAgenteAbierto(true)
                      }}
                      className="btn-secondary"
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      onClick={() => eliminarAgente(agente.id)}
                      className="btn-danger"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Resto de pestañas (salas, modelos) - mantener código existente */}
        {/* ... */}
      </main>

      {/* Modales */}
      
      {/* Modal Subir Archivo */}
      <Dialog open={modalSubirArchivo} onOpenChange={setModalSubirArchivo}>
        <DialogContent className="modal-glass">
          <DialogHeader>
            <DialogTitle className="text-white">📁 Subir Archivo</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-gray-400">
              Sube archivos que los agentes podrán consultar y analizar
            </p>
            <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-400 mb-4">Selecciona un archivo para subir</p>
              <input
                ref={inputArchivoRef}
                type="file"
                onChange={manejarSubidaArchivo}
                className="hidden"
                accept=".pdf,.doc,.docx,.txt,.xlsx,.xls,.png,.jpg,.jpeg"
              />
              <Button
                onClick={() => inputArchivoRef.current?.click()}
                disabled={cargandoArchivo}
                className="btn-primary"
              >
                {cargandoArchivo ? 'Subiendo...' : 'Seleccionar Archivo'}
              </Button>
            </div>
            <p className="text-xs text-gray-500">
              Formatos soportados: PDF, Word, Excel, TXT, imágenes
            </p>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal Armario */}
      <Dialog open={modalArmario} onOpenChange={setModalArmario}>
        <DialogContent className="modal-glass">
          <DialogHeader>
            <DialogTitle className="text-white">🗄️ Agregar al Armario</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-gray-400">
              Agrega documentos al armario para que estén disponibles en todas las salas de reuniones
            </p>
            <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center">
              <Archive className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-400 mb-4">Selecciona un documento para el armario</p>
              <input
                ref={inputArmarioRef}
                type="file"
                onChange={manejarSubidaArmario}
                className="hidden"
                accept=".pdf,.doc,.docx,.txt,.xlsx,.xls,.png,.jpg,.jpeg"
              />
              <Button
                onClick={() => inputArmarioRef.current?.click()}
                disabled={cargandoArchivo}
                className="btn-primary"
              >
                {cargandoArchivo ? 'Subiendo...' : 'Seleccionar Documento'}
              </Button>
            </div>
            <p className="text-xs text-gray-500">
              Los documentos del armario estarán disponibles para consulta en todas las salas
            </p>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal Búsqueda Web */}
      <Dialog open={modalBusquedaWeb} onOpenChange={setModalBusquedaWeb}>
        <DialogContent className="modal-glass">
          <DialogHeader>
            <DialogTitle className="text-white">🔍 Búsqueda Web Avanzada</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Consulta de búsqueda
              </label>
              <input
                type="text"
                value={busquedaWeb}
                onChange={(e) => setBusquedaWeb(e.target.value)}
                placeholder="Escribe tu consulta..."
                className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="flex space-x-4">
              <Button
                onClick={realizarBusquedaWeb}
                disabled={cargandoBusqueda || !busquedaWeb.trim()}
                className="btn-primary flex-1"
              >
                {cargandoBusqueda ? 'Buscando...' : 'Buscar'}
              </Button>
              <Button
                onClick={() => setModalBusquedaWeb(false)}
                className="btn-secondary"
              >
                Cancelar
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

// Función auxiliar para toggle de aprendizaje
const toggleAprendizaje = (agenteId) => {
  setAgentes(prev => prev.map(a => 
    a.id === agenteId ? { ...a, aprendiendo: !a.aprendiendo } : a
  ))
}

// Función auxiliar para eliminar agente
const eliminarAgente = (agenteId) => {
  const agente = agentes.find(a => a.id === agenteId)
  if (!agente) return

  if (confirm(`¿Eliminar el agente "${agente.nombre}"?`)) {
    setAgentes(prev => prev.filter(a => a.id !== agenteId))
    alert(`🗑️ Agente "${agente.nombre}" eliminado`)
  }
}

export default App

