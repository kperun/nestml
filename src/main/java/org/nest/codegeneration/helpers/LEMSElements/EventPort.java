package org.nest.codegeneration.helpers.LEMSElements;

import org.nest.nestml._ast.ASTInputLine;
import org.nest.nestml._ast.ASTOutput;
import org.reflections.vfs.CommonsVfs2UrlType;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;

/**
 * This class represents an input or output-port, an interface derived from buffers stated in the source-model.
 * This class has to be altered if the concept of current or spike-buffers became supported by LEMS.
 *
 * @author perun
 */
public class EventPort {
  private String name;
  private Direction dir;

  /**
   * Creates a port from an input-buffer of the source-model.
   *
   * @param variable an input-buffer
   */
  public EventPort(ASTInputLine variable) {
    this.name = variable.getName();
    this.dir = Direction.in;
  }


	/**
     * This method can be used to generate an event port from a xml node.
     * @param xmlNode the event port xml node.
     */
  public EventPort(Node xmlNode){
    this.name = xmlNode.getAttributes().getNamedItem("name").getNodeValue();
    if(xmlNode.getAttributes().getNamedItem("direction").getNodeValue().equals("in")){
      this.dir = Direction.in;
    }
    else {
      this.dir = Direction.out;
    }
  }

  /**
   * Creates a port from an output-buffer of the source-model.
   *
   * @param variable an output-buffer
   */
  public EventPort(ASTOutput variable) {
    if (variable.isCurrent()) {
      this.name = "current";
    }
    else {
      this.name = "spike";
    }
    dir = Direction.out;
  }

  public String getName() {
    return this.name;
  }

  public Direction getDirection() {
    return this.dir;
  }

  public enum Direction {
    in, out
  }
}