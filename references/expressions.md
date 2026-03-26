# VB.NET Expressions Reference for UiPath

Common expressions used in UiPath workflows.

---

## String Operations

### Basic Operations
```vb
' Concatenation
"Hello " + strName
String.Concat("Value: ", strValue)
$"Hello {strName}"  ' String interpolation (VB 14+)

' Length
strText.Length

' Substring
strText.Substring(0, 5)           ' First 5 characters
strText.Substring(5)              ' From position 5 to end

' Contains/StartsWith/EndsWith
strText.Contains("search")
strText.StartsWith("prefix")
strText.EndsWith("suffix")

' Replace
strText.Replace("old", "new")

' Split
strText.Split(","c)               ' Returns String()
strText.Split({","}, StringSplitOptions.RemoveEmptyEntries)

' Trim
strText.Trim()
strText.TrimStart()
strText.TrimEnd()

' Case conversion
strText.ToUpper()
strText.ToLower()
strText.ToTitleCase()             ' Requires CultureInfo

' Null/Empty checks
String.IsNullOrEmpty(strText)
String.IsNullOrWhiteSpace(strText)
If(strText, "default")            ' Null coalescing
```

### String Formatting
```vb
' Format with placeholders
String.Format("Name: {0}, Age: {1}", strName, intAge)

' Number formatting
intValue.ToString("N2")           ' 1,234.56
dblValue.ToString("C")            ' $1,234.56
dblValue.ToString("P")            ' 12.34%
intValue.ToString("D5")           ' 00123 (padded)

' Date formatting
dtDate.ToString("yyyy-MM-dd")     ' 2024-01-15
dtDate.ToString("dd/MM/yyyy")     ' 15/01/2024
dtDate.ToString("MMMM dd, yyyy")  ' January 15, 2024
```

### Regex
```vb
' Match
System.Text.RegularExpressions.Regex.IsMatch(strText, "\d+")

' Extract
System.Text.RegularExpressions.Regex.Match(strText, "\d+").Value

' Replace
System.Text.RegularExpressions.Regex.Replace(strText, "\d+", "X")

' All matches
System.Text.RegularExpressions.Regex.Matches(strText, "\d+")
```

---

## DateTime Operations

### Current Date/Time
```vb
DateTime.Now                      ' Current date and time
DateTime.Today                    ' Today at midnight
DateTime.UtcNow                   ' UTC time
```

### Parsing
```vb
DateTime.Parse("2024-01-15")
DateTime.ParseExact("15/01/2024", "dd/MM/yyyy", Nothing)
DateTime.TryParse(strDate, dtResult)
```

### Date Arithmetic
```vb
dtDate.AddDays(7)
dtDate.AddMonths(1)
dtDate.AddYears(1)
dtDate.AddHours(24)
dtDate.AddMinutes(30)

' Difference
(dtEnd - dtStart).TotalDays
(dtEnd - dtStart).TotalHours
DateDiff(DateInterval.Day, dtStart, dtEnd)
```

### Date Components
```vb
dtDate.Year
dtDate.Month
dtDate.Day
dtDate.Hour
dtDate.Minute
dtDate.DayOfWeek
dtDate.DayOfYear
```

### Business Days
```vb
' Add business days (simplified)
Enumerable.Range(1, intDays).Aggregate(dtStart, Function(d, i)
  If d.AddDays(1).DayOfWeek = DayOfWeek.Saturday Then d.AddDays(3)
  ElseIf d.AddDays(1).DayOfWeek = DayOfWeek.Sunday Then d.AddDays(2)
  Else d.AddDays(1))
```

---

## Numeric Operations

### Conversion
```vb
CInt(strValue)                    ' To Integer
CDbl(strValue)                    ' To Double
CStr(intValue)                    ' To String
Convert.ToInt32(strValue)
Convert.ToDouble(strValue)
Integer.Parse(strValue)
Double.TryParse(strValue, dblResult)
```

### Math
```vb
Math.Abs(intValue)                ' Absolute value
Math.Round(dblValue, 2)           ' Round to 2 decimals
Math.Floor(dblValue)              ' Round down
Math.Ceiling(dblValue)            ' Round up
Math.Max(a, b)
Math.Min(a, b)
Math.Pow(base, exponent)
Math.Sqrt(value)
```

### Random
```vb
New Random().Next(1, 100)         ' Random int 1-99
New Random().NextDouble()         ' Random 0.0-1.0
```

---

## DataTable Operations

### Access Data
```vb
' Row count
dtData.Rows.Count

' Column count
dtData.Columns.Count

' Get cell value
dtData.Rows(0)("ColumnName").ToString()
dtData.Rows(0).Item("ColumnName").ToString()
row("ColumnName").ToString()      ' Inside ForEach row

' Check if column exists
dtData.Columns.Contains("ColumnName")
```

### Filter with Select
```vb
' Filter rows (returns DataRow())
dtData.Select("Status = 'Active'")
dtData.Select("Amount > 100")
dtData.Select("Name LIKE 'John%'")
dtData.Select("Date > #2024-01-01#")

' With sorting
dtData.Select("Status = 'Active'", "Name ASC")

' To DataTable
dtData.Select("Status = 'Active'").CopyToDataTable()
```

### LINQ Queries
```vb
' Filter
dtData.AsEnumerable().Where(Function(r) r("Status").ToString() = "Active")

' Select column
dtData.AsEnumerable().Select(Function(r) r("Name").ToString())

' Distinct values
dtData.AsEnumerable().Select(Function(r) r("Category").ToString()).Distinct()

' Sum
dtData.AsEnumerable().Sum(Function(r) CDbl(r("Amount")))

' Average
dtData.AsEnumerable().Average(Function(r) CDbl(r("Amount")))

' Count with condition
dtData.AsEnumerable().Count(Function(r) r("Status").ToString() = "Active")

' First/Last
dtData.AsEnumerable().First()
dtData.AsEnumerable().FirstOrDefault()
dtData.AsEnumerable().Last()

' Order by
dtData.AsEnumerable().OrderBy(Function(r) r("Name").ToString())
dtData.AsEnumerable().OrderByDescending(Function(r) CDbl(r("Amount")))

' Group by
dtData.AsEnumerable().GroupBy(Function(r) r("Category").ToString())

' To DataTable (after LINQ)
dtFiltered.CopyToDataTable()
```

### Modify DataTable
```vb
' Add column
dtData.Columns.Add("NewColumn", GetType(String))

' Add row
dtData.Rows.Add({"Value1", "Value2", "Value3"})
dtData.Rows.Add(row)

' Update cell
dtData.Rows(0)("ColumnName") = "NewValue"

' Delete row
dtData.Rows(0).Delete()
dtData.AcceptChanges()

' Remove column
dtData.Columns.Remove("ColumnName")

' Clear all rows
dtData.Clear()

' Clone structure (empty)
dtData.Clone()

' Copy with data
dtData.Copy()
```

---

## Dictionary Operations

### Create and Access
```vb
' Create
New Dictionary(Of String, Object)

' Add
dictConfig("Key") = "Value"
dictConfig.Add("Key", "Value")

' Get value
dictConfig("Key").ToString()
dictConfig.Item("Key").ToString()

' Check key exists
dictConfig.ContainsKey("Key")

' Get with default
If(dictConfig.ContainsKey("Key"), dictConfig("Key").ToString(), "default")

' Remove
dictConfig.Remove("Key")

' Clear
dictConfig.Clear()
```

### Iteration
```vb
' Keys
dictConfig.Keys

' Values
dictConfig.Values

' Key-value pairs (in ForEach)
kvp.Key
kvp.Value
```

---

## JSON Operations

### Parse JSON
```vb
' Using Newtonsoft.Json
Newtonsoft.Json.JsonConvert.DeserializeObject(Of JObject)(strJson)
Newtonsoft.Json.JsonConvert.DeserializeObject(Of JArray)(strJsonArray)

' Access values
jObject("property").ToString()
jObject("nested")("property").ToString()
jArray(0)("property").ToString()

' Check property exists
jObject.ContainsKey("property")
jObject("property") IsNot Nothing
```

### Create JSON
```vb
' Create object
New JObject(New JProperty("name", strName), New JProperty("value", intValue))

' Serialize
Newtonsoft.Json.JsonConvert.SerializeObject(objData)
```

---

## QueueItem Operations

### Access SpecificContent
```vb
' Get field
in_TransactionItem.SpecificContent("FieldName").ToString()

' Check field exists
in_TransactionItem.SpecificContent.ContainsKey("FieldName")

' Get with default
If(in_TransactionItem.SpecificContent.ContainsKey("FieldName"),
   in_TransactionItem.SpecificContent("FieldName").ToString(),
   "default")
```

### QueueItem Properties
```vb
in_TransactionItem.Reference
in_TransactionItem.Priority
in_TransactionItem.Status
in_TransactionItem.CreationTime
in_TransactionItem.DeferDate
in_TransactionItem.DueDate
in_TransactionItem.RetryNumber
```

---

## File Path Operations

```vb
' Combine paths
Path.Combine(strFolder, strFileName)

' Get parts
Path.GetFileName(strPath)         ' "file.txt"
Path.GetFileNameWithoutExtension(strPath)  ' "file"
Path.GetExtension(strPath)        ' ".txt"
Path.GetDirectoryName(strPath)    ' "C:\Folder"

' Check exists
File.Exists(strPath)
Directory.Exists(strPath)

' Get files
Directory.GetFiles(strFolder)
Directory.GetFiles(strFolder, "*.txt")
Directory.GetFiles(strFolder, "*.txt", SearchOption.AllDirectories)
```

---

## Null Handling

```vb
' Check null
variable Is Nothing
variable IsNot Nothing

' Null coalescing
If(variable, "default")
If(variable IsNot Nothing, variable.ToString(), "default")

' Safe navigation (VB doesn't have ?. but can use If)
If(obj IsNot Nothing, obj.Property, Nothing)
```

---

## Common Patterns

### Try Convert with Default
```vb
If(Integer.TryParse(strValue, intResult), intResult, 0)
If(DateTime.TryParse(strDate, dtResult), dtResult, DateTime.MinValue)
```

### Safe Dictionary Access
```vb
If(dictConfig.ContainsKey("Key"), dictConfig("Key").ToString(), "")
```

### Safe QueueItem Field Access
```vb
If(in_TransactionItem.SpecificContent.ContainsKey("Field"),
   in_TransactionItem.SpecificContent("Field").ToString(),
   "")
```

### Build Log Message
```vb
$"[{strProcessName}] {strState} - {strMessage}"
String.Format("[{0}] {1} - {2}", strProcessName, strState, strMessage)
```
