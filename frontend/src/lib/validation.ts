import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(1, "Password is required."),
});
export type LoginFormValues = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
  fullName: z.string().min(1, "Full name is required.").max(120),
  email: z.string().email("Enter a valid email address."),
  password: z
    .string()
    .min(12, "Password must be at least 12 characters.")
    .regex(/[A-Za-z]/, "Password must include a letter.")
    .regex(/\d/, "Password must include a digit."),
});
export type RegisterFormValues = z.infer<typeof registerSchema>;

export const workspaceSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters.").max(80),
  description: z.string().max(500).optional(),
});
export type WorkspaceFormValues = z.infer<typeof workspaceSchema>;

export const projectSchema = z.object({
  name: z.string().min(1, "Project name is required.").max(120),
  description: z.string().max(2000).optional(),
  repository_url: z
    .string()
    .max(500)
    .refine((v) => !v || v.startsWith("http://") || v.startsWith("https://") || v.startsWith("git@"), {
      message: "Must be an http(s) or git URL.",
    })
    .optional()
    .or(z.literal("")),
  environment: z.enum(["development", "staging", "production"]),
  business_criticality: z.enum(["low", "medium", "high", "critical"]),
});
export type ProjectFormValues = z.infer<typeof projectSchema>;
