using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;

using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;

using RevitApplication = Autodesk.Revit.ApplicationServices.Application;
using WinForms = System.Windows.Forms;


namespace Pvs.RevitTools
{
    /// <summary>
    /// Dávkové načtení Project Base Point z lokálních RVT souborů.
    ///
    /// Příkaz:
    /// 1. nabídne výběr složky,
    /// 2. vyhledá RVT soubory,
    /// 3. postupně je otevře přes Revit API,
    /// 4. načte hodnoty Project Base Point,
    /// 5. uloží CSV report,
    /// 6. dokumenty zavře bez uložení.
    /// </summary>
    [Transaction(TransactionMode.Manual)]
    [Regeneration(RegenerationOption.Manual)]
    public class BatchPbpCommand : IExternalCommand
    {
        public Result Execute(
            ExternalCommandData commandData,
            ref string message,
            ElementSet elements)
        {
            UIApplication uiApplication = commandData.Application;
            RevitApplication application = uiApplication.Application;

            string selectedFolder = SelectFolder();

            if (string.IsNullOrWhiteSpace(selectedFolder))
            {
                return Result.Cancelled;
            }

            bool includeSubfolders = AskForSubfolders();

            SearchOption searchOption = includeSubfolders
                ? SearchOption.AllDirectories
                : SearchOption.TopDirectoryOnly;

            List<string> rvtFiles;

            try
            {
                rvtFiles = Directory
                    .EnumerateFiles(selectedFolder, "*.rvt", searchOption)
                    .Where(IsCandidateRvtFile)
                    .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
                    .ToList();
            }
            catch (Exception exception)
            {
                TaskDialog.Show(
                    "Batch PBP",
                    "Nepodařilo se načíst obsah složky.\n\n" +
                    exception.Message);

                return Result.Failed;
            }

            if (rvtFiles.Count == 0)
            {
                TaskDialog.Show(
                    "Batch PBP",
                    "Ve vybrané složce nebyly nalezeny žádné RVT soubory.");

                return Result.Cancelled;
            }

            TaskDialogResult continueResult = ShowStartSummary(
                selectedFolder,
                includeSubfolders,
                rvtFiles.Count);

            if (continueResult != TaskDialogResult.Yes)
            {
                return Result.Cancelled;
            }

            List<PbpResult> results = new List<PbpResult>();

            foreach (string rvtPath in rvtFiles)
            {
                PbpResult result = ProcessRvtFile(
                    application,
                    rvtPath);

                results.Add(result);
            }

            string reportPath = CreateReportPath(selectedFolder);

            try
            {
                WriteCsvReport(reportPath, results);
            }
            catch (Exception exception)
            {
                message =
                    "Modely byly zpracovány, ale nepodařilo se uložit CSV.\n" +
                    exception.Message;

                TaskDialog.Show("Batch PBP", message);

                return Result.Failed;
            }

            int successfulCount = results.Count(
                item => item.Status == "OK");

            int errorCount = results.Count - successfulCount;

            TaskDialog completionDialog = new TaskDialog("Batch PBP");

            completionDialog.MainInstruction =
                "Dávkové načtení Project Base Point bylo dokončeno.";

            completionDialog.MainContent =
                "Celkem modelů: " + results.Count + "\n" +
                "Úspěšně: " + successfulCount + "\n" +
                "S chybou: " + errorCount + "\n\n" +
                "Report:\n" + reportPath;

            completionDialog.CommonButtons =
                TaskDialogCommonButtons.Close;

            completionDialog.Show();

            return Result.Succeeded;
        }


        /// <summary>
        /// Zobrazí dialog pro výběr složky.
        /// </summary>
        private static string SelectFolder()
        {
            using (WinForms.FolderBrowserDialog dialog =
                   new WinForms.FolderBrowserDialog())
            {
                dialog.Description =
                    "Vyberte složku obsahující RVT modely.";

                dialog.ShowNewFolderButton = false;

                WinForms.DialogResult result = dialog.ShowDialog();

                if (result != WinForms.DialogResult.OK)
                {
                    return null;
                }

                return dialog.SelectedPath;
            }
        }


        /// <summary>
        /// Zeptá se, zda procházet také podsložky.
        /// </summary>
        private static bool AskForSubfolders()
        {
            TaskDialog dialog = new TaskDialog("Batch PBP");

            dialog.MainInstruction =
                "Mají se prohledat také podsložky?";

            dialog.MainContent =
                "Ano: načtou se RVT ze zvolené složky i všech podsložek.\n" +
                "Ne: načtou se pouze RVT přímo ve zvolené složce.";

            dialog.CommonButtons =
                TaskDialogCommonButtons.Yes |
                TaskDialogCommonButtons.No;

            dialog.DefaultButton =
                TaskDialogResult.Yes;

            return dialog.Show() == TaskDialogResult.Yes;
        }


        /// <summary>
        /// Souhrn před zahájením zpracování.
        /// </summary>
        private static TaskDialogResult ShowStartSummary(
            string selectedFolder,
            bool includeSubfolders,
            int fileCount)
        {
            TaskDialog dialog = new TaskDialog("Batch PBP");

            dialog.MainInstruction =
                "Spustit dávkové načtení Project Base Point?";

            dialog.MainContent =
                "Složka:\n" + selectedFolder + "\n\n" +
                "Podsložky: " +
                (includeSubfolders ? "ANO" : "NE") + "\n" +
                "Počet RVT: " + fileCount + "\n\n" +
                "Dokumenty budou otevřeny pouze pro čtení dat " +
                "a následně zavřeny bez uložení.";

            dialog.CommonButtons =
                TaskDialogCommonButtons.Yes |
                TaskDialogCommonButtons.No;

            dialog.DefaultButton =
                TaskDialogResult.Yes;

            return dialog.Show();
        }


        /// <summary>
        /// Filtruje záložní a dočasné soubory.
        /// </summary>
        private static bool IsCandidateRvtFile(string path)
        {
            string fileName = Path.GetFileName(path);

            if (string.IsNullOrWhiteSpace(fileName))
            {
                return false;
            }

            if (fileName.StartsWith("~", StringComparison.OrdinalIgnoreCase))
            {
                return false;
            }

            if (fileName.EndsWith(
                ".0001.rvt",
                StringComparison.OrdinalIgnoreCase))
            {
                return false;
            }

            // Filtrace běžných záložních souborů:
            // Model.0001.rvt, Model.0002.rvt apod.
            string nameWithoutExtension =
                Path.GetFileNameWithoutExtension(fileName);

            if (nameWithoutExtension.Length >= 5)
            {
                string possibleBackupSuffix =
                    nameWithoutExtension.Substring(
                        nameWithoutExtension.Length - 5);

                if (possibleBackupSuffix.StartsWith("."))
                {
                    string number =
                        possibleBackupSuffix.Substring(1);

                    if (number.All(char.IsDigit))
                    {
                        return false;
                    }
                }
            }

            return true;
        }


        /// <summary>
        /// Zpracuje jeden RVT soubor.
        /// </summary>
        private static PbpResult ProcessRvtFile(
            RevitApplication application,
            string rvtPath)
        {
            PbpResult result = new PbpResult
            {
                FileName = Path.GetFileName(rvtPath),
                FullPath = rvtPath,
                Status = "ERROR"
            };

            Document document = null;

            try
            {
                if (!File.Exists(rvtPath))
                {
                    throw new FileNotFoundException(
                        "Soubor nebyl nalezen.",
                        rvtPath);
                }

                BasicFileInfo basicInfo =
                    BasicFileInfo.Extract(rvtPath);

                result.SavedInRevitVersion =
                    basicInfo.Format;

                result.IsWorkshared =
                    basicInfo.IsWorkshared;

                result.IsCentral =
                    basicInfo.IsCentral;

                result.IsLocal =
                    basicInfo.IsLocal;

                ModelPath modelPath =
                    ModelPathUtils.ConvertUserVisiblePathToModelPath(
                        rvtPath);

                OpenOptions openOptions =
                    CreateOpenOptions(basicInfo.IsWorkshared);

                document = application.OpenDocumentFile(
                    modelPath,
                    openOptions);

                if (document == null)
                {
                    throw new InvalidOperationException(
                        "Revit nevrátil otevřený dokument.");
                }

                if (document.IsFamilyDocument)
                {
                    result.Status = "SKIPPED";
                    result.Error =
                        "Soubor je rodina RFA nebo family document.";

                    return result;
                }

                ReadProjectBasePoint(document, result);
                ReadProjectLocation(document, result);

                result.Status = "OK";
                result.Error = string.Empty;

                return result;
            }
            catch (Exception exception)
            {
                result.Status = "ERROR";
                result.Error =
                    exception.GetType().Name + ": " +
                    exception.Message;

                return result;
            }
            finally
            {
                if (document != null && document.IsValidObject)
                {
                    try
                    {
                        // false = zavřít bez uložení
                        document.Close(false);
                    }
                    catch (Exception closeException)
                    {
                        if (string.IsNullOrWhiteSpace(result.Error))
                        {
                            result.Error =
                                "Chyba při zavírání: " +
                                closeException.Message;
                        }
                        else
                        {
                            result.Error +=
                                " | Chyba při zavírání: " +
                                closeException.Message;
                        }
                    }
                }
            }
        }


        /// <summary>
        /// Nastavení otevírání RVT.
        /// U workshared modelů zavře uživatelské worksety,
        /// aby se snížila paměťová náročnost.
        /// </summary>
        private static OpenOptions CreateOpenOptions(
            bool isWorkshared)
        {
            OpenOptions options = new OpenOptions
            {
                Audit = false,
                AllowOpeningLocalByWrongUser = true
            };

            if (isWorkshared)
            {
                options.DetachFromCentralOption =
                    DetachFromCentralOption.DoNotDetach;

                WorksetConfiguration worksetConfiguration =
                    new WorksetConfiguration(
                        WorksetConfigurationOption.CloseAllWorksets);

                options.SetOpenWorksetsConfiguration(
                    worksetConfiguration);
            }

            return options;
        }


        /// <summary>
        /// Načte Project Base Point.
        /// </summary>
        private static void ReadProjectBasePoint(
            Document document,
            PbpResult result)
        {
            BasePoint projectBasePoint =
                BasePoint.GetProjectBasePoint(document);

            if (projectBasePoint == null)
            {
                throw new InvalidOperationException(
                    "Project Base Point nebyl nalezen.");
            }

            result.PbpElementId =
                projectBasePoint.Id.Value;

            // Parametry Project Base Point.
            result.EastWestMeters = GetLengthParameterInMeters(
                projectBasePoint,
                BuiltInParameter.BASEPOINT_EASTWEST_PARAM);

            result.NorthSouthMeters = GetLengthParameterInMeters(
                projectBasePoint,
                BuiltInParameter.BASEPOINT_NORTHSOUTH_PARAM);

            result.ElevationMeters = GetLengthParameterInMeters(
                projectBasePoint,
                BuiltInParameter.BASEPOINT_ELEVATION_PARAM);

            result.AngleToTrueNorthDegrees =
                GetAngleParameterInDegrees(
                    projectBasePoint,
                    BuiltInParameter.BASEPOINT_ANGLETON_PARAM);

            /*
             * Fyzická pozice prvku BasePoint v interních
             * souřadnicích dokumentu.
             *
             * Tato hodnota se může významově lišit od zobrazených
             * parametrů N/S, E/W a Elevation.
             */
            XYZ position = projectBasePoint.Position;

            result.PbpPositionXmeters =
                InternalLengthToMeters(position.X);

            result.PbpPositionYmeters =
                InternalLengthToMeters(position.Y);

            result.PbpPositionZmeters =
                InternalLengthToMeters(position.Z);

            /*
             * SharedPosition představuje polohu bodu
             * ve sdíleném souřadnicovém systému dokumentu.
             */
            XYZ sharedPosition =
                projectBasePoint.SharedPosition;

            result.PbpSharedXmeters =
                InternalLengthToMeters(sharedPosition.X);

            result.PbpSharedYmeters =
                InternalLengthToMeters(sharedPosition.Y);

            result.PbpSharedZmeters =
                InternalLengthToMeters(sharedPosition.Z);
        }


        /// <summary>
        /// Načte ProjectPosition v Internal Origin.
        /// Slouží jako doplňková kontrola transformace
        /// aktivního ProjectLocation.
        /// </summary>
        private static void ReadProjectLocation(
            Document document,
            PbpResult result)
        {
            ProjectLocation projectLocation =
                document.ActiveProjectLocation;

            if (projectLocation == null)
            {
                return;
            }

            result.ProjectLocationName =
                projectLocation.Name;

            XYZ internalOrigin = XYZ.Zero;

            ProjectPosition projectPosition =
                projectLocation.GetProjectPosition(
                    internalOrigin);

            if (projectPosition == null)
            {
                return;
            }

            result.ProjectLocationEastWestMeters =
                InternalLengthToMeters(
                    projectPosition.EastWest);

            result.ProjectLocationNorthSouthMeters =
                InternalLengthToMeters(
                    projectPosition.NorthSouth);

            result.ProjectLocationElevationMeters =
                InternalLengthToMeters(
                    projectPosition.Elevation);

            result.ProjectLocationAngleDegrees =
                RadiansToDegrees(
                    projectPosition.Angle);
        }


        /// <summary>
        /// Načte délkový parametr a převede interní stopy na metry.
        /// </summary>
        private static double? GetLengthParameterInMeters(
            Element element,
            BuiltInParameter builtInParameter)
        {
            Parameter parameter =
                element.get_Parameter(builtInParameter);

            if (parameter == null ||
                !parameter.HasValue ||
                parameter.StorageType != StorageType.Double)
            {
                return null;
            }

            return UnitUtils.ConvertFromInternalUnits(
                parameter.AsDouble(),
                UnitTypeId.Meters);
        }


        /// <summary>
        /// Načte úhlový parametr a převede radiány na stupně.
        /// </summary>
        private static double? GetAngleParameterInDegrees(
            Element element,
            BuiltInParameter builtInParameter)
        {
            Parameter parameter =
                element.get_Parameter(builtInParameter);

            if (parameter == null ||
                !parameter.HasValue ||
                parameter.StorageType != StorageType.Double)
            {
                return null;
            }

            return RadiansToDegrees(
                parameter.AsDouble());
        }


        private static double InternalLengthToMeters(
            double internalValue)
        {
            return UnitUtils.ConvertFromInternalUnits(
                internalValue,
                UnitTypeId.Meters);
        }


        private static double RadiansToDegrees(
            double radians)
        {
            return radians * 180.0 / Math.PI;
        }


        /// <summary>
        /// Vytvoří jedinečný název CSV reportu.
        /// </summary>
        private static string CreateReportPath(
            string selectedFolder)
        {
            string timestamp =
                DateTime.Now.ToString(
                    "yyyyMMdd_HHmmss",
                    CultureInfo.InvariantCulture);

            string fileName =
                "PBP_Report_" + timestamp + ".csv";

            return Path.Combine(
                selectedFolder,
                fileName);
        }


        /// <summary>
        /// Uloží CSV jako UTF-8 BOM se středníkem.
        /// Formát je vhodný pro český Excel.
        /// </summary>
        private static void WriteCsvReport(
            string reportPath,
            IEnumerable<PbpResult> results)
        {
            Encoding encoding =
                new UTF8Encoding(true);

            using (StreamWriter writer =
                   new StreamWriter(reportPath, false, encoding))
            {
                writer.WriteLine(
                    string.Join(";",
                        "Soubor",
                        "Cesta",
                        "Stav",
                        "Chyba",
                        "Verze Revitu",
                        "Workshared",
                        "Central",
                        "Local",
                        "PBP ElementId",
                        "PBP V/Z E-W [m]",
                        "PBP S/Z N-S [m]",
                        "PBP výška [m]",
                        "PBP úhel [°]",
                        "PBP Position X [m]",
                        "PBP Position Y [m]",
                        "PBP Position Z [m]",
                        "PBP Shared X [m]",
                        "PBP Shared Y [m]",
                        "PBP Shared Z [m]",
                        "ProjectLocation",
                        "ProjectLocation E-W [m]",
                        "ProjectLocation N-S [m]",
                        "ProjectLocation výška [m]",
                        "ProjectLocation úhel [°]"
                    ));

                foreach (PbpResult result in results)
                {
                    writer.WriteLine(
                        string.Join(";",
                            Csv(result.FileName),
                            Csv(result.FullPath),
                            Csv(result.Status),
                            Csv(result.Error),
                            Csv(result.SavedInRevitVersion),
                            Csv(BoolText(result.IsWorkshared)),
                            Csv(BoolText(result.IsCentral)),
                            Csv(BoolText(result.IsLocal)),
                            Csv(result.PbpElementId),
                            CsvNumber(result.EastWestMeters),
                            CsvNumber(result.NorthSouthMeters),
                            CsvNumber(result.ElevationMeters),
                            CsvNumber(result.AngleToTrueNorthDegrees),
                            CsvNumber(result.PbpPositionXmeters),
                            CsvNumber(result.PbpPositionYmeters),
                            CsvNumber(result.PbpPositionZmeters),
                            CsvNumber(result.PbpSharedXmeters),
                            CsvNumber(result.PbpSharedYmeters),
                            CsvNumber(result.PbpSharedZmeters),
                            Csv(result.ProjectLocationName),
                            CsvNumber(
                                result.ProjectLocationEastWestMeters),
                            CsvNumber(
                                result.ProjectLocationNorthSouthMeters),
                            CsvNumber(
                                result.ProjectLocationElevationMeters),
                            CsvNumber(
                                result.ProjectLocationAngleDegrees)
                        ));
                }
            }
        }


        private static string BoolText(bool? value)
        {
            if (!value.HasValue)
            {
                return string.Empty;
            }

            return value.Value ? "ANO" : "NE";
        }


        private static string CsvNumber(double? value)
        {
            if (!value.HasValue)
            {
                return string.Empty;
            }

            return Csv(
                value.Value.ToString(
                    "0.000000",
                    CultureInfo.CurrentCulture));
        }


        private static string Csv(long? value)
        {
            return value.HasValue
                ? Csv(value.Value.ToString(
                    CultureInfo.InvariantCulture))
                : string.Empty;
        }


        /// <summary>
        /// Bezpečný zápis CSV položky.
        /// </summary>
        private static string Csv(string value)
        {
            if (string.IsNullOrEmpty(value))
            {
                return string.Empty;
            }

            string escaped =
                value.Replace("\"", "\"\"");

            return "\"" + escaped + "\"";
        }
    }


    /// <summary>
    /// Datový objekt jednoho řádku reportu.
    /// </summary>
    internal class PbpResult
    {
        public string FileName { get; set; }
        public string FullPath { get; set; }

        public string Status { get; set; }
        public string Error { get; set; }

        public string SavedInRevitVersion { get; set; }

        public bool? IsWorkshared { get; set; }
        public bool? IsCentral { get; set; }
        public bool? IsLocal { get; set; }

        public long? PbpElementId { get; set; }

        public double? EastWestMeters { get; set; }
        public double? NorthSouthMeters { get; set; }
        public double? ElevationMeters { get; set; }
        public double? AngleToTrueNorthDegrees { get; set; }

        public double? PbpPositionXmeters { get; set; }
        public double? PbpPositionYmeters { get; set; }
        public double? PbpPositionZmeters { get; set; }

        public double? PbpSharedXmeters { get; set; }
        public double? PbpSharedYmeters { get; set; }
        public double? PbpSharedZmeters { get; set; }

        public string ProjectLocationName { get; set; }

        public double? ProjectLocationEastWestMeters { get; set; }
        public double? ProjectLocationNorthSouthMeters { get; set; }
        public double? ProjectLocationElevationMeters { get; set; }
        public double? ProjectLocationAngleDegrees { get; set; }
    }
}