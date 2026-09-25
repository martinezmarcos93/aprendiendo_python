"""
Límites de recursos para el subproceso que corre el código del chico.

En Linux/macOS los pone el padre con `resource` (ver proceso.py). Windows no tiene `resource`:
acá el propio subproceso se mete en un Job Object con tope de memoria (ctypes, sin dependencias).
Así un `x es "a" * 10000000000` termina con un MemoryError explicado y no congela la compu.
"""
import sys

MEMORIA_MAX = 512 * 1024 * 1024
_JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x100
_JobObjectExtendedLimitInformation = 9


def limitar_memoria_windows(maximo=MEMORIA_MAX):
    """Pone tope de memoria (bytes) al proceso actual. Devuelve True si quedó aplicado.
    Si algo falla (otro sistema, o un Job que no admite anidarse) devuelve False: es una protección extra,
    no debe impedir que el programa corra."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        from ctypes import wintypes

        class _Contadores(ctypes.Structure):
            _fields_ = [(n, ctypes.c_ulonglong) for n in (
                "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

        class _Basico(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
                        ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class _Extendido(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", _Basico), ("IoInfo", _Contadores),
                        ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.CreateJobObjectW.restype = wintypes.HANDLE
        k.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        k.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        k.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        k.GetCurrentProcess.restype = wintypes.HANDLE

        trabajo = k.CreateJobObjectW(None, None)
        if not trabajo:
            return False
        info = _Extendido()
        info.BasicLimitInformation.LimitFlags = _JOB_OBJECT_LIMIT_PROCESS_MEMORY
        info.ProcessMemoryLimit = int(maximo)
        if not k.SetInformationJobObject(trabajo, _JobObjectExtendedLimitInformation, ctypes.byref(info), ctypes.sizeof(info)):
            return False
        return bool(k.AssignProcessToJobObject(trabajo, k.GetCurrentProcess()))
    except Exception:            # noqa: BLE001 — la protección extra nunca debe romper la ejecución
        return False
