
/*

A problem asked by Google.

Given a list of numbers and a number k, return whether any two numbers from the list add up to k.

*/
import java.util.Arrays;

/**
* @author Jeff Bailey
* 
**/
 public class ArrayManipulation {


  /**
  * Returns true if numbers add to k
  * Returns false if no numbers add to k
  * @param inputArray The array to check.
  * @param k The number to check the inputArray with.
  */
  public static boolean containsNumberPairWithSum(int[] inputArray, int k) {
    boolean result = false;
    Arrays.sort(inputArray);
    // j is the previous number in the array
    for (int i = 0, j = inputArray.length - 1; i < j;) {
      int sum = inputArray[i] + inputArray[j];
      if (sum < k)
        i++;
      else if (sum > k)
        j--;
      else
        return true;
    }
    return result;
  }
}