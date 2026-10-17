// AnalizadorPDF
public class AnalizadorPDF
{
    public void Analizar()
    {
        AbrirArchivo();          // <-- copia
        ExtraerDatos();          // <-- copia (aunque el contenido cambia)
        ProcesarDatos();         // <-- copia
        CerrarArchivo();         // <-- copia
    }
    private void AbrirArchivo() => Console.WriteLine("Abriendo PDF...");
    private void ExtraerDatos() => Console.WriteLine("Extrayendo texto del PDF");
    private void ProcesarDatos() => Console.WriteLine("Procesando datos comunes");
    private void CerrarArchivo() => Console.WriteLine("Cerrando PDF...");
}

// AnalizadorDOC
public class AnalizadorDOC
{
    public void Analizar()
    {
        AbrirArchivo();          // <-- copia
        ExtraerDatos();          // <-- copia (aunque el contenido cambia)
        ProcesarDatos();         // <-- copia
        CerrarArchivo();         // <-- copia
    }
    private void AbrirArchivo() => Console.WriteLine("Abriendo DOC...");
    private void ExtraerDatos() => Console.WriteLine("Extrayendo texto del DOC");
    private void ProcesarDatos() => Console.WriteLine("Procesando datos comunes");
    private void CerrarArchivo() => Console.WriteLine("Cerrando DOC...");
}

// AnalizadorCSV
public class AnalizadorCSV
{
    public void Analizar()
    {
        AbrirArchivo();          // <-- copia
        ExtraerDatos();          // <-- copia (aunque el contenido cambia)
        ProcesarDatos();         // <-- copia
        CerrarArchivo();         // <-- copia
    }
    private void AbrirArchivo() => Console.WriteLine("Abriendo CSV...");
    private void ExtraerDatos() => Console.WriteLine("Extrayendo filas del CSV");
    private void ProcesarDatos() => Console.WriteLine("Procesando datos comunes");
    private void CerrarArchivo() => Console.WriteLine("Cerrando CSV...");
}