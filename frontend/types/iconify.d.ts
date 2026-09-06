import React from "react";

declare global {
  namespace JSX {
    interface IntrinsicElements {
      "iconify-icon": React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          icon?: string;
          class?: string;
          inline?: boolean;
          width?: string | number;
          height?: string | number;
        },
        HTMLElement
      >;
    }
  }
}
