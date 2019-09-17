
import java.io.*;
import java.util.*;

public class Solution{
  static final int OUTPUT_ROWS = 800_000,
                   MAX_FILE_SIZE = 349_000_000;  // make sure < 350 MB
  
  // set to true to allow accessing ground truth data in order to determine
  // distinct values for state-dependent columns
  static final boolean findDistinctStateValues = true;
  
  SplittableRandom rnd;
    
  int nColumns, nGroups;
  Field[] fields = null;
  int[] nBins = null;
  
  HashMap<String, Integer> fieldNameToColumn = new HashMap<>();
  ArrayList<FieldGroup> fieldGroups;
  HashSet<Integer> usedFields;
   
  void run(String inDataFilename, String outDataFilename,
            HashMap<String, Field> specs, 
            double epsilon){
    
    // pre-processing //////////////////////////////////////////////////////////
    
    System.out.println(String.format("Using epsilon = %3.2f", epsilon));
    
    // use a different random sequence every run
    rnd = new SplittableRandom();  
    
    String dataHeaderLine;
    String[] dataHeader;
    fieldGroups = new ArrayList<>();
    usedFields = new HashSet<>();
    
    // read data file
    ArrayList<String> data = new ArrayList<>();
    try (BufferedReader br = new BufferedReader(
            new FileReader(inDataFilename))){
      dataHeaderLine = br.readLine();
      dataHeader = dataHeaderLine.split(",", -1);
      for (int col = 0; col < dataHeader.length; col++)
        fieldNameToColumn.put(dataHeader[col], col);
      
      // define bins and column arrays
      nColumns = dataHeader.length;
      nBins = new int[nColumns];
      fields = new Field[nColumns];
      
      for (String line; (line = br.readLine()) != null; ) data.add(line);
    }catch (Exception e){ 
      System.err.println(e); 
      System.err.println("Error reading data.");
      return;
    }
    
    // determine distinct values for state-dependent columns 
    if (findDistinctStateValues){
      String[] names = { "SEA", "METAREA", "COUNTY", "CITY", "METAREAD" };
      int n = names.length;
      
      // find columns fields are in
      int[] columns = { -1, -1, -1, -1, -1 };
      for (int col = 0; col < nColumns; col++)
        for (int i = 0; i < n; i++)
          if (dataHeader[col].equals(names[i])){
            columns[i] = col;
            specs.get(names[i]).reset();  
          }
      
      // assign distinct values to fields
      for (String line : data){
        String[] row = line.split(",", -1);
        for (int i = 0; i < names.length; i++)
          if (columns[i] >= 0){
            int value = Integer.parseInt(row[columns[i]]);
            if (!specs.get(names[i]).valueToBin.containsKey(value))
              specs.get(names[i]).addValue(value);
          }
      }
    }
        
    for (int col = 0; col < nColumns; col++){
      Field field = specs.get(dataHeader[col]);
        
      // define some bins for fields not in codebook
      switch(field.name){
        case "SUPDIST":
          field.setBins(10, 630, 10);
          break;
        case "MIGSEA5":
          field.setBins(1, 502, 1,  990, 991, 1,  997, 997, 1);
          break;
        case "INCWAGE":
          field.setBins(0, 5000, 1,  999998, 999998, 1);
          break;
        case "VALUEH":
          field.setBins(0, 30000, 1,  9999998, 9999999, 1);
          break;
        case "EDSCOR50":
          field.setBins(0, 1000, 1,  9999, 9999, 1);
          break;
        case "ERSCOR50":
          field.setBins(0, 1000, 1,  9999, 9999, 1);
          break;
        case "MIGMET5":
          field.setBins(0, 9600, 20,  9999, 9999, 1);
          break;
        case "MIGCOUNTY":
          field.setBins(0, 8000, 10,  9997, 9999, 2);
          break;
        case "NPBOSS50":
          field.setBins(0, 1000, 1,  9999, 9999, 1);
          break;
        case "IND":
          field.setBins(0, 231, 1,  995, 995, 1,  998, 999, 1);
          break;
        default:
          break;
      }
      
      // determine number of bins and field type for column
      if (field.type.equals("enum")){
        if (field.valueToBin == null)
          // if value bins not defined set to all values from 0 to maxval
          nBins[col] = field.maxval + 1;
        else
          nBins[col] = field.valueToBin.size();
        
        fields[col] = field;
      }else{
        System.out.println("UNEXPECTED TYPE!");
      }
    }
      
    // combine correlated fields into groups
    addGroup("SPLIT", "OWNERSHP", "GQ", "GQTYPE", "OWNERSHPD",
            "GQFUNDS", "GQTYPED");
    addGroup("VETWWI", "SLREC", "SSENROLL", "NATIVITY", "VETPER",
            "VET1940", "UCLASSWK", "VETCHILD", "VETSTAT", "VETSTATD");
    addGroup("RESPONDT", "CITIZEN", "MARST", "NCHLT5", "FAMSIZE");
    addGroup("URBAN", "FARM", "WARD", "CITYPOP");
    addGroup("LABFORCE", "SCHOOL", "SEX", "EMPSTAT", "CLASSWKR", 
            "INCNONWG", "EMPSTATD", "CLASSWKRD");
    addGroup("SPANNAME", "HISPAN", "HISPRULE", "HISPAND");
    addGroup("METRO", "METAREA", "METAREAD");
    addGroup("RACE", "RACED");
    addGroup("WKSWORK2", "WKSWORK1");
    addGroup("HRSWORK2", "HRSWORK1");
    addGroup("SAMESEA5", "SAMEPLAC", "MIGTYPE5", "MIGRATE5", "MIGRATE5D");
    addGroup("MARRNO", "CHBORN");
    addGroup("SIZEPL", "URBPOP");
    addGroup("SEA", "CITY");
    addGroup("SUPDIST", "COUNTY");
    addGroup("OCCSCORE", "EDSCOR50");
    addGroup("MTONGUE", "MTONGUED");
    addGroup("SEI", "PRESGL");
    addGroup("HIGRADE", "EDUC", "HIGRADED", "EDUCD");
    addGroup("MBPL", "MBPLD");
    addGroup("FBPL", "FBPLD");
    addGroup("BPL", "BPLD");
    addGroup("IND1950", "IND");
    addGroup("MIGSEA5", "MIGPLAC5");
    addGroup("OCC", "OCC1950");
    addGroup("UOCC95", "UIND", "UOCC");
      
    // add any remaining fields into single sized groups
    for (int i = 0; i < nColumns; i++) 
      if (!usedFields.contains(i)) addGroup(i);
    
    nGroups = fieldGroups.size();
    System.out.println("Total field groups: " + nGroups);
      
    // fill bins
    for (String line : data){
      String[] row = line.split(",", -1);
      for (FieldGroup group : fieldGroups) group.add(row);
    }
    
    // privatization ///////////////////////////////////////////////////////////
    
    // add noise
    // divide total epsilon equally for each FieldGroup's histogram of counts
    // --> epsilon per group = (total epsilon)/(number of groups)
    // --> scale = 1/(epsilon per group) = (number of groups)/(total epsilon)
    double scale = nGroups/epsilon;
    
    // add Laplacian noise with scale = nGroups/epsilon to every counts bin
    for (FieldGroup group : fieldGroups) group.privatize(scale);
    
    // post-processing /////////////////////////////////////////////////////////
    
    // create data
    int fileSize = 0;
    try (PrintWriter pw = new PrintWriter(outDataFilename)){
      fileSize+= dataHeaderLine.length() + 1;
      
      // write header
      pw.write(dataHeaderLine + "\n");
      
      for (int row = 0; row < OUTPUT_ROWS; row++){
        
        // get noisy count weighted random values for each column
        int[] colValues = new int[nColumns];
        for (FieldGroup group : fieldGroups){
          int[] values = group.getRandomValues();
          for (int i = 0; i < values.length; i++)
            colValues[group.columns[i]] = values[i];
        }
        
        // add values for the row to a string
        String s = "";
        for (int col = 0; col < nColumns; col++)
          s+= (col > 0 ? "," : "") + colValues[col];
        
        s+= "\n";
        
        // stop if output file would be too large
        fileSize+= s.length();
        if (fileSize > MAX_FILE_SIZE) break;
        
        // write row
        pw.write(s);
      }
    }catch (Exception e){ System.err.println(e); }
  }
  
  // add another FieldGroup using names to choose fields
  void addGroup(String...names){
    // if field name is present in data header, add to group
    ArrayList<Integer> colList = new ArrayList<>();
    for (String name : names)
      if(fieldNameToColumn.containsKey(name))
        colList.add(fieldNameToColumn.get(name));
    
    // if no fields are present then do nothing
    if (colList.isEmpty()) return;
    
    int[] columns = new int[colList.size()];
    for (int i = 0; i < columns.length; i++) 
      columns[i] = colList.get(i);
    
    addGroup(columns);
  }
  
  // add another FieldGroup using columns to choose fields
  void addGroup(int...columns){
    fieldGroups.add(new FieldGroup(columns));
    for (int i : columns){
      if (usedFields.contains(i)) 
        System.err.println("Field column " + i + " already used!");
      else 
        usedFields.add(i);
    }
  }
  
  // Field Group: fields grouped together share a single counts histogram
  public class FieldGroup{
    int[] columns;
    long[] counts;
    
    FieldGroup(int...columns){
      this.columns = columns;
      int totalBins = 1;
      for (int col : columns) totalBins*= nBins[col];
      counts = new long[totalBins];
    }
    
    // add a count to the correct bin
    void add(String[] row){
      int bin = 0, totalBins = 1;
      for (int col : columns){
        bin+= totalBins * fields[col].getBin(Integer.parseInt(row[col]));
        totalBins*= nBins[col];
      }
      counts[bin]++;
    }
  
    // add Laplacian noise to all counts bins
    // add previous bins counts to greatly improve speed of getRandomValues()
    //   by enabling use of a binary search
    void privatize(double scale){
      double threshold = 1.9*scale*Math.log10(counts.length);
      for (int bin = 0; bin < counts.length; bin++){
        double noise = Main.laplace(rnd, scale),
               dpbin = counts[bin] + noise;
        counts[bin] = dpbin < threshold ? 0 : (int)Math.round(dpbin);
        if (bin > 0) counts[bin]+= counts[bin-1];
      }
    }
    
    // get random values for each column in the group
    // values in returned array correspond to columns in columns[] array
    int[] getRandomValues(){
      int[] values = new int[columns.length];
      if (counts[counts.length-1] > 0){
        
        // use binary search to get noisy counts weighted random bin
        long r = rnd.nextLong(counts[counts.length-1]);
        int bin = Arrays.binarySearch(counts, r);
        if (bin < 0){
          bin = -bin-1;
        }else{
          bin++;
          while (bin < counts.length && counts[bin]==counts[bin-1]) bin++;
        }
        
        // get values for each column corresponding to the random bin
        int totalBins = 1;
        for (int iCol = 0; iCol < columns.length; iCol++){
          int col = columns[iCol];
          values[iCol] = fields[col].getValue((bin/totalBins) % nBins[col]);
          totalBins*= nBins[col];
        }
      }
      return values;
    }
  }
  
}
