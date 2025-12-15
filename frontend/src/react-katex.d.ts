declare module "react-katex" {
  import * as React from "react";

  export interface InlineMathProps {
    math: string;
    errorColor?: string;
  }

  export interface BlockMathProps {
    math: string;
    errorColor?: string;
  }

  export const InlineMath: React.FC<InlineMathProps>;
  export const BlockMath: React.FC<BlockMathProps>;
}
