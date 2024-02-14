
import java.io.*;
import java.util.*;

public class Main{
  static final String codebookPath = "codebook.cbk";
  
  // Laplace distribution: f(x) = 1/(2*scale)*exp(-|x|/scale)
  public static double laplace(SplittableRandom rnd, double scale){
    return scale*Math.log(rnd.nextDouble())*(rnd.nextInt(2) == 0 ? -1 : 1);
  }
  
  // read data specs from the .json file to a map of fieldname -> Field object
  public static HashMap<String, Field> 
        readSpecInfo(String specs, String codebook){
    HashMap<String, Field> info = new HashMap<>();
    
    try (BufferedReader br = new BufferedReader(new FileReader(specs))){
      
      // get map of fields from the .json specs file
      Field currentField = null;
      for (String line; (line = br.readLine()) != null; ){
        String[] s = line.split(":");
        if (s.length != 2) continue;
        for (int i = 0; i < s.length; i++){
          s[i] = s[i].trim();
          if (s[i].charAt(s[i].length()-1) == ',')
            s[i] = s[i].substring(0, s[i].length()-1);
        }
        if (s[1].equals("{")){
          String label = s[0].substring(1, s[0].length()-1);
          currentField = new Field();
          currentField.name = label;
          info.put(label, currentField);
        }else if (currentField != null){
          String name = s[0].substring(1, s[0].length()-1);
          switch(name){
            case "type":
              currentField.type = s[1].substring(1, s[1].length()-1);
              break;
            case "maxval":
              currentField.maxval = Integer.parseInt(s[1]);
              break;
            default:
              System.err.println("INVALID FIELD!");
              break;
          }
        }
      }
    }catch (Exception e){ System.err.println(e); }
    
    // get field bins from the codebook
    String currentLabel = null;
    boolean labelUsed = false;
    try (BufferedReader br = new BufferedReader(new FileReader(codebook))){
      for (String line; (line = br.readLine()) != null; ){
        String[] s = line.split("\t");
        if (s[0].length() >= 2 && s[0].charAt(0) == ' ' && 
            s[0].charAt(1) != ' '){
          currentLabel = s[0].trim();
          labelUsed = info.containsKey(currentLabel);
        }else if (labelUsed && s[0].length() > 0 && 
                  Character.isDigit(s[0].charAt(0))){
          info.get(currentLabel).addValue(Integer.parseInt(s[0]));
        }
      }
    }catch (Exception e){ System.err.println(e); }
    
    // make sure maxval is a bin
    for (String label : info.keySet()){
      Field field = info.get(label);
      if (field.valueToBin != null &&
          !field.valueToBin.containsKey(field.maxval))
        field.addValue(field.maxval);
    }
      
    return info;
  }
        
  static void runCommandLine(String[] args){
    // create synthetic datasets for epsilon = 8.0, 1.0 and 0.3
    if (args.length == 2){
      String inputFile = args[0], specsFile = args[1];
      HashMap<String, Field> specInfo = readSpecInfo(specsFile, codebookPath);
      
      Solution solution = new Solution();
      
      solution.run(inputFile, "8_0.csv", specInfo, 8.0);
      System.out.println("Synthetic data saved to 8_0.csv\n");
      
      solution.run(inputFile, "1_0.csv", specInfo, 1.0);
      System.out.println("Synthetic data saved to 1_0.csv\n");
      
      solution.run(inputFile, "0_3.csv", specInfo, 0.3);
      System.out.println("Synthetic data saved to 0_3.csv\n");
      
    // save synthetic dataset to args[2] using epsilon = args[3]
    }else if (args.length == 4){
      String inputFile = args[0], 
             specsFile = args[1],
             outputFile = args[2];
      double epsilon = Double.parseDouble(args[3]);
      Solution solution = new Solution();
      solution.run(inputFile, outputFile, 
              readSpecInfo(specsFile, codebookPath), epsilon);
      System.out.println("Synthetic data saved to " + outputFile);
      System.out.println();
    
    // display instructions if an invalid number of arguments are used
    }else{
      System.out.println("NistDp3 - synthetic data creation");
      System.out.println("syntax:");
      System.out.println("  java -jar NistDp3.jar <input file> " +
              "<specs file> [<output file> <epsilon>]");
      System.out.println();
      System.out.println("  If <output file> and <epsilon> are omitted, " +
              "outputs using epsilon = 8.0, 1.0 and 0.3");
      System.out.println("    will be saved to 8_0.csv, 1_0.csv and 0_3.csv");
    }
  }
  
  public static void main(String[] args){
    runCommandLine(args);
  }
  
}
