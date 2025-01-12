import React, { act } from "react";
import { render, renderHook, screen, waitFor } from "@testing-library/react";
import { AuthProvider, useAuth } from "./AuthContext";
import { getUser } from "./Services";
import { MemoryRouter } from "react-router";

jest.mock("./Services");

describe("AuthProvider", () => {
	beforeEach(() => {
		localStorage.clear();
		getUser.mockResolvedValueOnce({ data: { is_admin: true } });
	});

	it("should render AuthProvider without crashing", () => {
		render(
			<MemoryRouter>
				<AuthProvider>
					<div>Test Component</div>
				</AuthProvider>
			</MemoryRouter>
		);
		expect(screen.getByText("Test Component")).toBeInTheDocument();
	});

	it("should update the token and store in localStorage when setToken is called", async () => {
		const { result } = renderHook(useAuth, {
			wrapper: ({ children }) => (
				<MemoryRouter>
					<AuthProvider>{children}</AuthProvider>
				</MemoryRouter>
			),
		});
		act(() => {
			result.current.setToken("newToken");
		});

		expect(localStorage.getItem("token")).toBe("newToken");
	});

});

