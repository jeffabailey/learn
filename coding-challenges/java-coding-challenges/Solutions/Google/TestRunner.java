import org.junit.runner.JUnitCore;
import org.junit.runner.Result;
import org.junit.runner.notification.Failure;
import static com.diogonunes.jcolor.Ansi.colorize;
import static com.diogonunes.jcolor.Attribute.*;

public class TestRunner {
  public static void main() {
    Result testResult = JUnitCore.runClasses(ArrayManipulationTest.class);
    
    for (Failure failure : testResult.getFailures()) {
      System.out.println(failure.toString());
    }
    
    if(testResult.wasSuccessful()) {
      System.out.println(colorize("All tests in ArrayManipulationTest passed.",BLUE_TEXT())) ; 
    }
  }
}