
import java.util.*;

public class Field{
  String name, type;
  int maxval;
  ArrayList<Integer> values;
  HashMap<Integer, Integer> valueToBin;
  
  void reset(){ 
    values = new ArrayList<>(); 
    valueToBin = new HashMap<>(); 
  }
  
  void addValue(int value){
    if (values == null) reset();
    values.add(value);
    valueToBin.put(value, values.size() - 1);
  }
  
  // get histogram bin for value
  int getBin(int value){
    if (valueToBin == null) return value;
    Integer bin = valueToBin.get(value);
    // if value not in codebook use first bin
    return bin == null ? 0 : bin;
  }
  
  // get value corresponding to bin value
  int getValue(int bin){
    return values == null ? bin : (int)values.get(bin);
  }
  
  // set value ranges for undefined fields
  // params are value ranges: first0, last0, step0, first1, last1, step1, ....
  void setBins(int ... ranges){
    reset();
    
    for (int i = 0; i < ranges.length; i+= 3){
      int first = ranges[i], last = ranges[i+1], step = ranges[i+2];
      for (int j = first; j <= last; j+= step)
        addValue(j);
    }
  }
}
