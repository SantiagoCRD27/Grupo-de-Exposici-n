// Superclase
public abstract class AnalizadorArchivo
{
    public void Analizar()
    {
        AbrirArchivo();      // paso variable -> lo define la subclase
        ExtraerDatos();      // paso variable -> lo define la subclase
        ProcesarDatos();     // paso común  -> vive AQUÍ una sola vez
        CerrarArchivo();     // paso común  -> vive AQUÍ una sola vez
        MostrarReporte();    // hook opcional con implementación por defecto
    }

    // Pasos que OBLIGATORIAMENTE se van a cambiar segun el formato
    protected abstract void AbrirArchivo();
    protected abstract void ExtraerDatos();

    // Pasos comunes: se escriben UNA vez y se heredan
    protected virtual void ProcesarDatos()
        => Console.WriteLine("Procesando datos comunes (auditoría Sector 04)");

    protected virtual void CerrarArchivo()
        => Console.WriteLine("Cerrando archivo con protocolo de seguridad");

    // Hook: trae implementación por defecto, la subclase decide si le pone drama
    protected virtual void MostrarReporte()
        => Console.WriteLine("Reporte estándar listo.");
}