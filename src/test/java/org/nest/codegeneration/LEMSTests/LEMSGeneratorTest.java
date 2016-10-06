package org.nest.codegeneration.LEMSTests;

import org.junit.Test;
import org.nest.base.ModelbasedTest;
//import org.nest.frontend.NESTMLFrontend;

/**
 * Tests whether model can be generated without any critical errors (e.g. exceptions) and whether
 * the frontend works correctly.
 * @author perun
 */
public class LEMSGeneratorTest extends ModelbasedTest {
  private static final String INPUT_DIRECTORY = "src/test/resources/codegeneration/testSim";
  //NESTMLFrontend fe = new NESTMLFrontend();

  @Test
  public void testGenerateLEMS() throws Exception {
    String args[] = {INPUT_DIRECTORY,"-lems","-target build",
        "-config"+INPUT_DIRECTORY+"/config","-units_external","-simSteps0.1"};
    //fe.start(args);
  }
}