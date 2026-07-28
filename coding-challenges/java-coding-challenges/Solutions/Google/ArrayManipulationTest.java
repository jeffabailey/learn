import org.junit.Test;
import static org.junit.Assert.assertEquals;

import java.util.ArrayList;
import java.util.HashMap;

public class ArrayManipulationTest {

  // Begin: Given a list of numbers and a number k, return whether any two numbers from the list add up to k.
  // See ArrayManipulation::containsNumberPairWithSum
  @Test
  public void containsPairWithSumEmptyArray() {
    // arrange
    int[] emptyArray = {};
    int k = 1;

    ArrayManipulation arrayManipulation = new ArrayManipulation();

    // act
    boolean result = arrayManipulation.containsNumberPairWithSum(emptyArray, k);

    // assert
    assertEquals(result, false);
  }

  public void containsPairWithSumWithOnePair() {
    // arrange
    int[] arrayWithPair = { 1, 2 };
    int k = 1;

    ArrayManipulation arrayManipulation = new ArrayManipulation();

    // act
    boolean result = arrayManipulation.containsNumberPairWithSum(arrayWithPair, k);

    // assert
    assertEquals(result, true);
  }

  // End: Given a list of numbers and a number k, return whether any two numbers from the list add up to k.  
}