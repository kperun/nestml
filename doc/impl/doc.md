# PyNestML - NestML Toolchain in Python

**Disclaimer**: This documentation represents PyNestML's implementation "as it is". **No guarantee of completeness or correctness is given.** As typical for all types of software, the actual implementation may change over time. The following documentation, therefore, provides an overview of the used components and approaches, while the actual code may be adapted in future. Nonetheless, the general ideas and concepts should remain applicable and valid.

Engineering of domain-specific languages (DSL) such as NestML represents a process which requires a fundamental understanding in two areas: The problem domain (e.g., computational neuroscience), and a set of tools to model and solve problems in this domain. In the following, we will leave all principles related to the former to the experts of the respective domain, and only demonstrate how the latter can be solved by means of a set of generated and hand-coded solutions. Consequently, no discussion of modeled aspects takes place, the language is therefore assumed to be given. Instead, we will demonstrate, starting from the specification of the language, which components are required and how these components have been implemented in PyNestML.

[Section 1](front.md) introduces the model processing frontend, a subsystem which is able to read in a (textual) model and instantiate a computer processable representation. [Section 2](middle.md) will subsequently demonstrate a set of assisting components which make interaction with the tool, as well as other tasks, easier to achieve. [Section 3](back.md) will then show how model-to-text transformations (i.e., code generation)  can be achieved. Finally, for those who are interested in extension points of PyNestML, [Sections 4](extensions.md) will subsume how the framework has to be adapted and extended to support new concepts in NestML.
  
For more DSL-related details, we refer to Fow10[^1] and Ben16[^2].


[^1]: Martin Fowler. Domain-specific languages. Pearson Education, 2010.
[^2]: Benoit Combemale, Robert France and Jean-Marc Jezequel,  Bernhard Rumpe, James Steel and Didier Vojtisek. Engineering modeling languages: Turning domain knowledge into tools, 2016, CRC Press